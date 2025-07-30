def hello():
    print("Hello, Pixegami!")


def program3():
    code = """
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_iris

iris = load_iris()
x = pd.DataFrame(iris.data, columns=iris.feature_names)
y = pd.Series(iris.target).map(dict(enumerate(iris.target_names)))

X_scaled = StandardScaler().fit_transform(x)
X_pca = PCA(n_components=2).fit_transform(X_scaled)
pca_df = pd.DataFrame(X_pca, columns=['pc1', 'pc2'])
pca_df['species'] = y

plt.figure(figsize=(8,6))
sns.scatterplot(data=pca_df, x='pc1', y='pc2', hue='species', palette='deep')
plt.title("PCA of Iris Dataset")
plt.show()

print("Explained Variance Ratio: ", PCA(n_components=2).fit(X_scaled).explained_variance_ratio_)
"""
    print(code)
