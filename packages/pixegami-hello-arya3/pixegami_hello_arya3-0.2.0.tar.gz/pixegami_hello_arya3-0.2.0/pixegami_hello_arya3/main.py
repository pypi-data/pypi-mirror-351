def hello():
    print("Hello, Pixegami!")

def program1():
    code = '''
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns 
from sklearn.datasets import fetch_california_housing 

# Step 1: Load dataset 
data = fetch_california_housing() 
df = pd.DataFrame(data.data, columns=data.feature_names) 
df['Target'] = data.target 

# Step 2: Plot Histograms 
df.hist(bins=30, figsize=(15, 10), edgecolor='black') 
plt.suptitle("Histograms of Numerical Features", fontsize=16) 
plt.tight_layout() 
plt.show() 

# Step 3: Plot Boxplots (each feature in its own subplot) 
plt.figure(figsize=(15, 10)) 
for i, feature in enumerate(df.columns): 
    plt.subplot(3, 3, i + 1) 
    sns.boxplot(x=df[feature], color='orange') 
    plt.title(f'Box Plot of {feature}') 
    plt.tight_layout() 
plt.show() 

# Step 4: Detect and Print Outliers using IQR 
print("\nOutliers per Feature:") 
for col in df.columns: 
    Q1, Q3 = df[col].quantile([0.25, 0.75]) 
    IQR = Q3 - Q1 
    lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR 
    outliers = df[(df[col] < lower) | (df[col] > upper)] 
    print(f"{col}: {len(outliers)} outliers") 


   '''
    print(code)

def program2():
    code = '''
import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt 
from sklearn.datasets import fetch_california_housing 

# Step 1: Load the California Housing Dataset 
# Option to load from CSV (commented out) 
# data = pd.read_csv('Add Your Dataset Path') 

# Load from sklearn 
housing = fetch_california_housing(as_frame=True) 
data = housing.frame 

# Preview the data 
print(data.head()) 

# Step 2: Compute the correlation matrix 
correlation_matrix = data.corr() 

# Step 3: Visualize the correlation matrix using a heatmap 
plt.figure(figsize=(10, 8)) 
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5) 
plt.title('Correlation Matrix of California Housing Features') 
plt.show() 

# Step 4: Create a pair plot to visualize pairwise relationships 
pair_plot = sns.pairplot(data, diag_kind='kde', plot_kws={'alpha': 0.5}) 
pair_plot.fig.suptitle('Pair Plot of California Housing Features', y=1.02) 
plt.show()


   '''
    print(code)

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


def program4():
    code = '''
import pandas as pd 
 
def find_s(examples): 
    """ 
    Find the most specific hypothesis that fits all positive examples. 
    Args: 
        examples (list of lists): Dataset with last column as target ('Yes'/'No') 
    Returns: 
        list: Final hypothesis 
    """ 
    hypothesis = ['0'] * (len(examples[0]) - 1)  # Initialize hypothesis 
     
    for x in examples: 
        if x[-1] == 'Yes':  # Consider only positive examples 
            for i in range(len(x) - 1): 
                if hypothesis[i] == '0': 
                    hypothesis[i] = x[i] 
                elif hypothesis[i] != x[i]: 
                    hypothesis[i] = '?' 
    return hypothesis 
 
# Local data option 
data = [['Sunny', 'Warm', 'Normal', 'Strong', 'Warm', 'Same', 'Yes'], 
        ['Sunny', 'Warm', 'High', 'Strong', 'Warm', 'Same', 'Yes'], 
        ['Rainy', 'Cold', 'High', 'Strong', 'Warm', 'Change', 'No'], 
        ['Sunny', 'Warm', 'High', 'Strong', 'Cool', 'Change', 'Yes']] 
 
# sklearn dataset option (commented) 
# from sklearn.datasets import load_iris 
# data = load_iris().data 
 
print("Final Hypothesis:", find_s(data))
'''
    print(code)


def program5():
    code = '''
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier

# Step 1: Generate data
np.random.seed(42)
X = np.random.rand(100, 1)
y = np.array(['Class1' if x <= 0.5 else 'Class2' for x in X.flatten()])

# Step 2: Split into training and testing
X_train, y_train = X[:50], y[:50]
X_test, y_test = X[50:], y[50:]

k_values = [1, 2, 3, 4, 5, 20, 30]

for k in k_values:
    model = KNeighborsClassifier(n_neighbors=k)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    plt.figure(figsize=(8, 5))
    
    # Plot training data on y=0, colored by true label
    colors_train = ['blue' if label == 'Class1' else 'red' for label in y_train]
    plt.scatter(X_train, np.zeros_like(X_train), c=colors_train, marker='o', label='Train Class1/2')
    
    # Separate test points by predicted class for plotting on y=1
    class1_test = X_test[y_pred == 'Class1']
    class2_test = X_test[y_pred == 'Class2']
    
    plt.scatter(class1_test, np.ones_like(class1_test), c='blue', marker='x', label='Test Predicted Class1')
    plt.scatter(class2_test, np.ones_like(class2_test), c='red', marker='x', label='Test Predicted Class2')
    
    plt.title(f'k-NN Classification (k={k})')
    plt.xlabel('Data Points')
    plt.ylabel('Classification Level')
    plt.yticks([0, 1], ['Train', 'Test'])
    plt.legend()
    plt.grid(True)
    
    accuracy = np.mean(y_pred == y_test)
    print(f"Accuracy for k={k}: {accuracy:.2f}")
    
    plt.show()

   '''
    print(code)


def program6():
    code = '''
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(64)

# Generate training data: noisy sine wave
X = np.linspace(-3, 3, 100).reshape(-1, 1)
y = np.sin(X).ravel() + np.random.normal(scale=0.1, size=X.shape[0])

def locally_weighted_regression(x_query, X_train, y_train, tau):
    # Compute weights based on distance from x_query (Gaussian kernel)
    W = np.exp(-((X_train - x_query) ** 2) / (2 * tau ** 2))
    
    # Add bias term (intercept)
    X_bias = np.c_[np.ones_like(X_train), X_train]
    
    # Create diagonal weight matrix
    W_diag = np.diag(W.ravel())
    
    # Weighted least squares solution: theta = (X' W X)^-1 X' W y
    theta = np.linalg.pinv(X_bias.T @ W_diag @ X_bias) @ X_bias.T @ W_diag @ y_train
    
    # Predict y for x_query (including bias)
    return np.array([1, x_query]) @ theta

# Test points for prediction
X_test = np.linspace(-3, 3, 100)

# Predict y values at test points using LWR
y_pred = np.array([locally_weighted_regression(x, X, y, tau=0.5) for x in X_test])

# Plot training data and LWR fit
plt.scatter(X, y, color="gray", alpha=0.5, label="Training Data")
plt.plot(X_test, y_pred, color="red", linewidth=2, label="LWR Fit (τ=0.5)")
plt.xlabel("x")
plt.ylabel("y")
plt.title("Locally Weighted Regression Fit")
plt.legend()
plt.grid(True)
plt.show()


   '''
    print(code)


def program7():
    code = '''
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.datasets import fetch_california_housing
import numpy as np

def linear_regression_california():
    # Load California Housing dataset
    housing = fetch_california_housing(as_frame=True)
    X = housing.data[['AveRooms']]  # Average rooms per household
    y = housing.target               # Median house value (in 100k USD)

    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

    model = LinearRegression().fit(X_train, y_train)
    y_pred = model.predict(X_test)

    plt.figure(figsize=(10, 5))
    plt.scatter(X_test, y_test, color='blue', label='Actual')
    plt.plot(X_test, y_pred, color='red', label='Predicted', linewidth=2)
    plt.title("Linear Regression - California Housing")
    plt.xlabel("Average Rooms (AveRooms)")
    plt.ylabel("Median House Value ($100,000s)")
    plt.legend()
    plt.show()

    print("Linear Regression - California Housing")
    print("MSE:", mean_squared_error(y_test, y_pred))
    print("R²:", r2_score(y_test, y_pred))


def polynomial_regression_auto():
    # Load Auto MPG dataset
    auto = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mpg.csv").dropna()
    X2 = auto[['horsepower']]
    y2 = auto['mpg']

    poly = PolynomialFeatures(degree=2)
    X2_poly = poly.fit_transform(X2)

    model2 = LinearRegression().fit(X2_poly, y2)
    
    # For smooth curve plotting, create sorted horsepower values
    X2_sorted = np.sort(X2.values, axis=0)
    X2_sorted_poly = poly.transform(X2_sorted)
    pred2_sorted = model2.predict(X2_sorted_poly)

    plt.figure(figsize=(10, 5))
    plt.scatter(X2, y2, label='Actual Data')
    plt.plot(X2_sorted, pred2_sorted, color='red', label='Polynomial Fit')
    plt.title("Polynomial Regression (Degree 2): Horsepower vs MPG")
    plt.xlabel("Horsepower")
    plt.ylabel("MPG")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    print("Demonstrating Linear & Polynomial Regression\n")
    linear_regression_california()
    polynomial_regression_auto()


   '''
    print(code)

def program8():
    code = '''
from sklearn.datasets import load_breast_cancer 
from sklearn.model_selection import train_test_split 
from sklearn.preprocessing import MinMaxScaler 
from sklearn.tree import DecisionTreeClassifier, plot_tree 
from sklearn.metrics import accuracy_score 
import matplotlib.pyplot as plt 
# Load data 
data = load_breast_cancer() 
X, y = data.data, data.target 
# Split data 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42) 
# Scale features 
scaler = MinMaxScaler() 
X_train_scaled = scaler.fit_transform(X_train) 
X_test_scaled = scaler.transform(X_test) 
# Train Decision Tree 
model = DecisionTreeClassifier(random_state=42) 
model.fit(X_train_scaled, y_train) 
# Predict and evaluate on test set 
y_pred = model.predict(X_test_scaled) 
print(f"Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%") 
# Plot the decision tree 
plt.figure(figsize=(15, 10)) 
plot_tree(model, filled=True, feature_names=data.feature_names, 
class_names=data.target_names, rounded=True) 
plt.title("Decision Tree Visualization") 
plt.show() 
# Classify new sample (using first test sample) 
new_sample = X_test[0].reshape(1, -1)  # reshape for single sample 
new_sample_scaled = scaler.transform(new_sample) 
new_pred = model.predict(new_sample_scaled) 
print(f"New sample prediction: {data.target_names[new_pred][0]}") 
print(f"Actual label for new sample: {data.target_names[y_test[0]]}")

   '''
    print(code)

def program9():
    code = '''
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_olivetti_faces
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Load dataset
X, y = fetch_olivetti_faces(shuffle=True, random_state=42, return_X_y=True)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train Naive Bayes classifier
model = GaussianNB()
model.fit(X_train, y_train)

# Predict on test set
y_pred = model.predict(X_test)

# Evaluation
print("LAB PROGRAM NO: 9 – Naive Bayesian Classifier\n")
print(f"Test Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
print(f"Cross-validation Accuracy: {cross_val_score(model, X, y, cv=5).mean() * 100:.2f}%\n")
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred, zero_division=1))

# Visualize predictions
fig, axes = plt.subplots(3, 5, figsize=(12, 8))
fig.suptitle("Sample Predictions", fontsize=14)
for ax, img, true, pred in zip(axes.ravel(), X_test[:15], y_test[:15], y_pred[:15]):
    ax.imshow(img.reshape(64, 64), cmap='gray')
    ax.set_title(f"T:{true} | P:{pred}", fontsize=8)
    ax.axis('off')
plt.tight_layout()
plt.subplots_adjust(top=0.88)
plt.show()


   '''
    print(code)

def program10():
    code = '''
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_breast_cancer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Load breast cancer dataset
data = load_breast_cancer()
X = data.data
feature_names = data.feature_names

# Convert to DataFrame
df = pd.DataFrame(X, columns=feature_names)

# Standardize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

# Apply KMeans clustering (2 clusters expected: malignant and benign)
kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_scaled)
df['Cluster'] = clusters

# Apply PCA to reduce to 2 dimensions for visualization
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
df['PCA1'] = X_pca[:, 0]
df['PCA2'] = X_pca[:, 1]

# Plotting
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='PCA1', y='PCA2', hue='Cluster', palette='viridis', s=80)

# Plot centroids in PCA space
centroids = kmeans.cluster_centers_
centroids_pca = pca.transform(centroids)
plt.scatter(centroids_pca[:, 0], centroids_pca[:, 1], c='red', marker='X', s=200, label='Centroids')

plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.title('K-Means Clustering on Breast Cancer Data')
plt.legend()
plt.tight_layout()
plt.show()


   '''
    print(code)

