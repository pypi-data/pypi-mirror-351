# Kura: Procedural API for Chat Data Analysis

![Kura Architecture](assets/images/kura-architecture.png)

Kura is an open-source library for understanding chat data through machine learning, inspired by [Anthropic's CLIO](https://www.anthropic.com/research/clio). It provides a functional, composable API for clustering conversations to discover patterns and insights.

## Why Analyze Conversation Data?

As AI assistants and chatbots become increasingly central to product experiences, understanding how users interact with these systems at scale becomes a critical challenge. Manually reviewing thousands of conversations is impractical, yet crucial patterns and user needs often remain hidden in this data.

Kura addresses this challenge by:

- **Revealing user intent patterns** that may not be obvious from individual conversations
- **Identifying common user needs** to prioritize feature development
- **Discovering edge cases and failures** that require attention
- **Tracking usage trends** over time as your product evolves
- **Informing prompt engineering** by highlighting successful and problematic interactions

## Features

- **Conversation Summarization**: Automatically generate concise task descriptions from conversations
- **Hierarchical Clustering**: Group similar conversations at multiple levels of granularity
- **Metadata Extraction**: Extract valuable context from conversations using LLMs
- **Custom Models**: Use your preferred embedding, summarization, and clustering methods
- **Checkpoint System**: Save and resume analysis sessions
- **Procedural API**: Functional approach with composable functions for maximum flexibility

## Installation

```bash
# Install from PyPI
pip install kura

# Or use uv for faster installation
uv pip install kura
```

## Quick Start

```python
from kura.v1 import (
    summarise_conversations,
    generate_base_clusters_from_conversation_summaries,
    reduce_clusters_from_base_clusters,
    reduce_dimensionality_from_clusters,
    CheckpointManager
)
from kura.types import Conversation
from kura.summarisation import SummaryModel
from kura.cluster import ClusterModel
from kura.meta_cluster import MetaClusterModel
from kura.dimensionality import HDBUMAP
import asyncio

# Load conversations
conversations = Conversation.from_hf_dataset(
    "ivanleomk/synthetic-gemini-conversations",
    split="train"
)

# Set up models
summary_model = SummaryModel()
cluster_model = ClusterModel()
meta_cluster_model = MetaClusterModel(max_clusters=10)
dimensionality_model = HDBUMAP()

# Set up checkpoint manager
checkpoint_mgr = CheckpointManager("./checkpoints", enabled=True)

# Run pipeline with explicit steps
async def process_conversations():
    # Step 1: Generate summaries
    summaries = await summarise_conversations(
        conversations,
        model=summary_model,
        checkpoint_manager=checkpoint_mgr
    )

    # Step 2: Create base clusters
    clusters = await generate_base_clusters_from_conversation_summaries(
        summaries,
        model=cluster_model,
        checkpoint_manager=checkpoint_mgr
    )

    # Step 3: Build hierarchy
    meta_clusters = await reduce_clusters_from_base_clusters(
        clusters,
        model=meta_cluster_model,
        checkpoint_manager=checkpoint_mgr
    )

    # Step 4: Project to 2D
    projected = await reduce_dimensionality_from_clusters(
        meta_clusters,
        model=dimensionality_model,
        checkpoint_manager=checkpoint_mgr
    )

    return projected

# Execute the pipeline
results = asyncio.run(process_conversations())
```

## Key Design Principles

### Function-Based Architecture
The procedural API follows the principle of **functions orchestrate, models execute**:
- Each pipeline step is a pure function with explicit inputs/outputs
- No hidden state or side effects
- Works with any model implementing the required interface

### Polymorphism Through Interfaces
All functions work with heterogeneous models:
- `BaseSummaryModel` - OpenAI, vLLM, Hugging Face, local models
- `BaseClusterModel` - HDBSCAN, KMeans, custom algorithms
- `BaseMetaClusterModel` - Different hierarchical strategies
- `BaseDimensionalityReduction` - UMAP, t-SNE, PCA

### Keyword-Only Arguments
All functions use keyword-only arguments for clarity and maintainability.

## Documentation

- **Getting Started**
  - [Installation Guide](getting-started/installation.md)
  - [Tutorial: Procedural API](getting-started/tutorial-procedural-api.md)

- **Core Concepts**
  - [Conversations](core-concepts/conversations.md)
  - [Embedding](core-concepts/embedding.md)
  - [Clustering](core-concepts/clustering.md)
  - [Summarization](core-concepts/summarization.md)
  - [Meta-Clustering](core-concepts/meta-clustering.md)
  - [Dimensionality Reduction](core-concepts/dimensionality-reduction.md)

- **API Reference**
  - [Procedural API Documentation](api/index.md)

## About

Kura is under active development. If you face any issues or have suggestions, please feel free to [open an issue](https://github.com/567-labs/kura/issues) or a PR. For more details on the technical implementation, check out this [walkthrough of the code](https://ivanleo.com/blog/understanding-user-conversations).
