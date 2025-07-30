# Marketing Measures

A Python package for scoring texts on 19 marketing dimensions using Hugging Face transformers.

- **Market Orientation** (8 dimensions):
customer orientation, competitor orientation, interfunctional coordination, longterm focus, profit focus, intelligence generation, intelligence dissemination, responsiveness

- **Marketing Capabilities** (8 dimensions):
information management, planning, implementation, pricing capabilities, product development, channel management, communication, selling capabilities

- **Marketing Excellence** (3 dimensions):
marketing ecosystem, end user, marketing agility

If you use this package in your research, please cite:
- Damavandi, Hoorsana, Mai, Feng, and Astvansh, Vivek (2025). A New Technique for Measuring a Firm's Marketing Emphasis. Marketing Letters.


## Installation

```bash
pip install marketing_measures
```

## Usage

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Marketing-Measures/marketing-measures/blob/main/examples/example.ipynb)


```python
import pandas as pd
from marketing_measures import MarketingEmphasisScorer

# Initialize the scorer
scorer = MarketingEmphasisScorer()

# Example texts covering various marketing aspects
texts = [
    "The firm uses AI to understand customer needs and preferences.",
    "We continuously scan the market to gather insights about competitors.",
    "Accurate customer analysis helps refine our marketing strategies.",
    "Market research revealed a gap in services that we can exploit.",
    "Collecting smart data enables more precise targeting.",
    "Our marketing strategy incorporates both traditional and digital channels.",
    "The team designed a creative campaign to boost brand awareness.",
    "We follow a structured marketing planning process each quarter.",
    "Segmentation allows us to tailor messages for different customer groups.",
    "The campaign exemplified out-of-the-box thinking to reach Gen Z consumers.",
    "Marketing KPIs are monitored weekly to ensure implementation is on track.",
    "Fast execution of campaigns helps us stay ahead of competitors.",
    "The team was highly responsive to market changes during the rollout.",
    "Resources were reallocated flexibly to maximize performance.",
    "Speed and adaptability are essential for successful marketing implementation.",
    "Our pricing strategy reflects deep knowledge of competitor price points.",
    "Dynamic pricing tools support our price setting capabilities.",
    "The team reviewed pricing insights before launching the new service.",
    "We adjusted prices based on customer feedback and pricing analytics.",
    "A strong pricing capability ensures we capture value without losing volume.",
    "R&D investment led to a novel solution for customer pain points.",
    "The product development team worked closely with users to refine features.",
    "Test marketing revealed high acceptance for the innovation.",
    "Commercialization of the new product was accelerated by effective planning.",
    "Innovation management is central to our long-term competitiveness.",
    "Strong distributor relationships enhance our reach in remote markets.",
    "We provide ongoing retailer support to improve product visibility.",
    "Retailer cooperation was key in launching the new product line.",
    "Channel management focuses on adding value across the supply chain.",
    "Partnering with intermediaries allowed faster market penetration.",
    "The advertising campaign increased brand awareness significantly.",
    "Our marketing communication strategy emphasizes consistent messaging.",
    "Public relations helped manage reputation during the crisis.",
    "Image and branding efforts are supported by coordinated promotion.",
    "We rely on integrated marketing communication for maximum impact.",
    "Salespeople are trained regularly to improve selling skills.",
    "Sales support tools help enable more effective customer interactions.",
    "The sales strategy focuses on value-based selling.",
    "Sales management ensures quotas are aligned with overall goals.",
    "Sales controlling enables better forecasting and performance evaluation.",
]

# Score texts using pre-trained ZCA transformers
results = scorer.score_texts(
    texts=texts,
    zca_transform="pre-trained",
    batch_size=32,
)

# Convert results to DataFrame for analysis
df = pd.DataFrame(results)
df["text"] = texts

# Focus on marketing capabilities dimensions
marketing_capability_dimensions = [
    "marketing information management",
    "marketing planning capabilities", 
    "marketing implementation capabilities",
    "pricing capabilities",
    "product development capabilities",
    "channel management",
    "marketing communication capabilities",
    "selling capabilities",
]

# Find top 3 sentences for each marketing capability dimension
for dimension in marketing_capability_dimensions:
    print(f"Top 3 sentences for {dimension}:")
    top_indices = df[dimension].nlargest(3).index
    for idx in top_indices:
        print(f"- {df['text'][idx]}")
    print()

# Get information about all available dimensions
print("All available dimensions:", model_info["all_dimension_names_in_order"])
```


### Additional Examples

**Example with DataFrame containing a text column:**
```python
import pandas as pd
from marketing_measures import MarketingEmphasisScorer

# Load or create a DataFrame with text data
df = pd.read_csv("data/example_data.csv")

# Initialize the scorer
scorer = MarketingEmphasisScorer()

# Score the text column
scores = scorer.score_texts(
    texts=df['text'].tolist(),
    zca_transform="pre-trained",
    batch_size=32,
)

# Add scores to the original DataFrame
scores_df = pd.DataFrame(scores)
result_df = pd.concat([df, scores_df], axis=1)

# Display results
print(result_df[['marketing ecosystem', 'end user', 'marketing agility']])
```

**Use a different embedding model** (from [Hugging Face](https://huggingface.co/spaces/mteb/leaderboard)):
```python
scorer = MarketingEmphasisScorer(model_name="mixedbread-ai/mxbai-embed-large-v1")
```

**Raw score without ZCA transformation**

*Note*: The Zero Component Analysis (ZCA) transformation is used to whiten the measures within each of the three constructs (Market Orientation, Marketing Capabilities, Marketing Excellence), which helps decorrelate and normalize the data. The pre-trained ZCA models were trained on executive presentations from earnings call transcripts spanning from 2003Q1 to 2023Q1. 

```python
scores_raw = scorer.score_texts(texts, zca_transform='none')
```

**Score and estimate ZCA from input data** (need larger dataset for better estimation)
```python
scores_zca_estimated, zca_models = scorer.score_texts(
    texts, 
    zca_transform='estimate', 
)
```