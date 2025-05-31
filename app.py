import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import zscore, ttest_ind, levene, shapiro, mannwhitneyu, kruskal
from GEOparse import get_GEO
import io
import zipfile
from PIL import Image

st.set_page_config(layout="wide")

st.title("🧬 Interactive Gene Expression Explorer")

@st.cache_data(show_spinner=True)
def load_data(dataset_id):
    try:
        gse = get_GEO(dataset_id, destdir=".")
        samples = gse.gsms

        expr_df = pd.DataFrame({gsm_name: gsm.table.set_index("ID_REF")["VALUE"]
                                for gsm_name, gsm in samples.items()})
        expr_df = expr_df.T
        expr_df.index.name = "sample_id"
        expr_df.reset_index(inplace=True)

        sample_info = []
        for gsm_name, gsm in samples.items():
            label = gsm.metadata.get("characteristics_ch1", ["unknown"])[0]
            sample_info.append((gsm_name, label))
        sample_df = pd.DataFrame(sample_info, columns=["sample_id", "label"])
        sample_df['label'] = sample_df['label'].str.replace(".*: ", "", regex=True)

        df = pd.merge(sample_df, expr_df, on="sample_id")
        return df, gse
        return None, None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None, None

# Sidebar
st.sidebar.header("Options")
dataset_id = st.sidebar.text_input("Enter GEO Dataset ID", value="GSE62945")

# Download section at top
if dataset_id:
    df, gse = load_data(dataset_id)
    if df is not None and gse is not None:
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button("📄 Download Full Data as CSV", csv_buffer.getvalue(), file_name=f"{dataset_id}_data.csv", mime="text/csv", type="primary")

        available_genes = df.columns[2:]
        gene = st.sidebar.selectbox("Select Gene", available_genes)

        # Dataset info
        st.subheader("🧬 Dataset Metadata")
        metadata = gse.metadata
        meta_table = pd.DataFrame({k: v[0] for k, v in metadata.items() if len(v) > 0}, index=[0]).T
        meta_table.columns = ["Value"]
        st.dataframe(meta_table, use_container_width=True, height=len(meta_table)*35)

        # Statistical summary
        st.subheader("📊 Summary Statistics")
        st.dataframe(df.groupby("label")[gene].describe())

        labels = df['label'].unique()
        stats_md = []
        if len(labels) == 2:
            group1 = df[df['label'] == labels[0]][gene]
            group2 = df[df['label'] == labels[1]][gene]

            stat_t, pval_t = ttest_ind(group1, group2, equal_var=False)
            stat_mw, pval_mw = mannwhitneyu(group1, group2)
            stat_levene, pval_levene = levene(group1, group2)
            pval_shapiro1 = shapiro(group1)[1]
            pval_shapiro2 = shapiro(group2)[1]

            stats_md.append(f"**T-test between {labels[0]} and {labels[1]}:** T = `{stat_t:.3f}`, p = `{pval_t:.4g}`")
            stats_md.append(f"**Mann-Whitney U Test:** U = `{stat_mw:.3f}`, p = `{pval_mw:.4g}`")
            stats_md.append(f"**Levene's Test for Equal Variance:** Statistic = `{stat_levene:.3f}`, p = `{pval_levene:.4g}`")
            stats_md.append("**Shapiro-Wilk Normality Test:**")
            stats_md.append(f"{labels[0]}: p = `{pval_shapiro1:.4g}`")
            stats_md.append(f"{labels[1]}: p = `{pval_shapiro2:.4g}`")

        elif len(labels) > 2:
            grouped = [df[df['label'] == label][gene] for label in labels]
            stat_kruskal, pval_kruskal = kruskal(*grouped)
            stats_md.append(f"**Kruskal-Wallis Test among groups:** Statistic = `{stat_kruskal:.3f}`, p = `{pval_kruskal:.4g}`")

        with st.expander("📐 Statistical Test Results"):
            for line in stats_md:
                st.markdown(line)

        st.subheader(f"📈 Expression Visualizations for Gene: `{gene}`")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📦 Boxplot")
            fig1, ax1 = plt.subplots(figsize=(5, 3))
            sns.boxplot(x='label', y=gene, data=df, ax=ax1)
            st.pyplot(fig1)

        with col2:
            st.markdown("#### 🎻 Violin Plot")
            fig2, ax2 = plt.subplots(figsize=(5, 3))
            sns.violinplot(x='label', y=gene, data=df, ax=ax2)
            st.pyplot(fig2)

        st.markdown("#### ✴️ Strip Plot")
        fig3, ax3 = plt.subplots(figsize=(7, 3))
        sns.stripplot(x='label', y=gene, data=df, jitter=True, ax=ax3)
        st.pyplot(fig3)

        st.markdown("#### 📉 Expression Across Samples")
        fig4, ax4 = plt.subplots(figsize=(7, 3))
        for label in labels:
            values = df[df['label'] == label][gene].values
            ax4.plot(np.arange(len(values)), values, label=label, marker='o')
        ax4.set_xlabel("Sample Index")
        ax4.set_ylabel("Expression Level")
        ax4.legend()
        ax4.grid(True)
        st.pyplot(fig4)

        st.markdown("#### 📊 Histogram")
        fig5, ax5 = plt.subplots(figsize=(7, 3))
        sns.histplot(data=df, x=gene, hue='label', kde=True, element="step", stat="density", ax=ax5)
        st.pyplot(fig5)

        st.markdown("#### 📈 CDF Plot")
        fig6, ax6 = plt.subplots(figsize=(7, 3))
        def plot_cdf(values, label):
            sorted_vals = np.sort(values)
            y = np.arange(len(sorted_vals)) / float(len(sorted_vals))
            ax6.plot(sorted_vals, y, label=label)

        for label in labels:
            values = df[df['label'] == label][gene].values
            plot_cdf(values, label)
        ax6.set_xlabel("Expression Level")
        ax6.set_ylabel("Cumulative Probability")
        ax6.legend()
        ax6.grid(True)
        st.pyplot(fig6)

        st.markdown("#### ⚖️ Z-Score Distribution")
        df['z_score'] = zscore(df[gene])
        fig7, ax7 = plt.subplots(figsize=(7, 3))
        sns.boxplot(x='label', y='z_score', data=df, ax=ax7)
        st.pyplot(fig7)

        st.subheader("🧠 Correlation Heatmap (Top 10 Genes by Variance)")
        top_genes = df[available_genes].var().sort_values(ascending=False).head(10).index
        corr = df[top_genes].corr()
        fig8, ax8 = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax8)
        st.pyplot(fig8)

        st.subheader("🔗 Pairplot of Top 4 Genes")
        with st.spinner("Generating pairplot (this may take a moment)..."):
            try:
                fig9 = sns.pairplot(df, vars=top_genes[:4], hue="label", height=2)
                st.pyplot(fig9)
            except Exception as e:
                st.warning(f"Pairplot could not be displayed: {e}")

        # Chart image downloads
        st.subheader("📸 Download All Charts")
        chart_buffers = []

        for i, fig in enumerate([fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8]):
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            chart_buffers.append((f"chart_{i+1}.png", buf.read()))

        if 'fig9' in locals():
            try:
                buf = io.BytesIO()
                fig9.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                buf.seek(0)
                chart_buffers.append(("chart_9_pairplot.png", buf.read()))
            except Exception as e:
                st.warning("Failed to export pairplot.")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for filename, content in chart_buffers:
                zipf.writestr(filename, content)
        zip_buffer.seek(0)

        st.download_button("🖼️ Download All Charts as ZIP", zip_buffer, file_name=f"{dataset_id}_charts.zip", mime="application/zip")
    else:
        st.warning("Failed to load dataset. Please check the GEO ID and try again.")
else:
    st.warning("Please enter a GEO dataset ID to begin.")