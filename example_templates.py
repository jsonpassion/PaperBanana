# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Example templates for PaperVizAgent Demo UI.
Each template contains a method section and caption for diagram generation.
"""

EXAMPLE_TEMPLATES = {
    "PaperVizAgent Framework": {
        "method": r"""## Methodology: The PaperVizAgent Framework

        In this section, we present the architecture of PaperVizAgent, a reference-driven agentic framework for automated academic illustration. As illustrated in Figure \ref{fig:methodology_diagram}, PaperVizAgent orchestrates a collaborative team of five specialized agents—Retriever, Planner, Stylist, Visualizer, and Critic—to transform raw scientific content into publication-quality diagrams and plots. (See Appendix \ref{app_sec:agent_prompts} for prompts)

### Retriever Agent

Given the source context $S$ and the communicative intent $C$, the Retriever Agent identifies $N$ most relevant examples $\mathcal{E} = \{E_n\}_{n=1}^{N} \subset \mathcal{R}$ from the fixed reference set $\mathcal{R}$ to guide the downstream agents. As defined in Section \ref{sec:task_formulation}, each example $E_i \in \mathcal{R}$ is a triplet $(S_i, C_i, I_i)$.
To leverage the reasoning capabilities of VLMs, we adopt a generative retrieval approach where the VLM performs selection over candidate metadata:
$$
\mathcal{E} = \text{VLM}_{\text{Ret}} \left( S, C, \{ (S_i, C_i) \}_{E_i \in \mathcal{R}} \right)
$$
Specifically, the VLM is instructed to rank candidates by matching both research domain (e.g., Agent & Reasoning) and diagram type (e.g., pipeline, architecture), with visual structure being prioritized over topic similarity. By explicitly reasoned selection of reference illustrations $I_i$ whose corresponding contexts $(S_i, C_i)$ best match the current requirements, the Retriever provides a concrete foundation for both structural logic and visual style.

### Planner Agent

The Planner Agent serves as the cognitive core of the system. It takes the source context $S$, communicative intent $C$, and retrieved examples $\mathcal{E}$ as inputs. By performing in-context learning from the demonstrations in $\mathcal{E}$, the Planner translates the unstructured or structured data in $S$ into a comprehensive and detailed textual description $P$ of the target illustration:
$$
P = \text{VLM}_{\text{plan}}(S, C, \{ (S_i, C_i, I_i) \}_{E_i \in \mathcal{E}})
$$

### Stylist Agent

To ensure the output adheres to the aesthetic standards of modern academic manuscripts, the Stylist Agent acts as a design consultant.
A primary challenge lies in defining a comprehensive "academic style," as manual definitions are often incomplete.
To address this, the Stylist traverses the entire reference collection $\mathcal{R}$ to automatically synthesize an *Aesthetic Guideline* $\mathcal{G}$ covering key dimensions such as color palette, shapes and containers, lines and arrows, layout and composition, and typography and icons (see Appendix \ref{app_sec:auto_summarized_style_guide} for the summarized guideline and implementation details). Armed with this guideline, the Stylist refines each initial description $P$ into a stylistically optimized version $P^*$:
$$
P^* = \text{VLM}_{\text{style}}(P, \mathcal{G})
$$
This ensures that the final illustration is not only accurate but also visually professional.

### Visualizer Agent

After receiving the stylistically optimized description $P^*$, the Visualizer Agent collaborates with the Critic Agent to render academic illustrations and iteratively refine their quality. The Visualizer Agent leverages an image generation model to transform textual descriptions into visual output. In each iteration $t$, given a description $P_t$, the Visualizer generates:
$$
I_t = \text{Image-Gen}(P_t)
$$
where the initial description $P_0$ is set to $P^*$.

### Critic Agent

The Critic Agent forms a closed-loop refinement mechanism with the Visualizer by closely examining the generated image $I_t$ and providing refined description $P_{t+1}$ to the Visualizer. Upon receiving the generated image $I_t$ at iteration $t$, the Critic inspects it against the original source context $(S, C)$ to identify factual misalignments, visual glitches, or areas for improvement. It then provides targeted feedback and produces a refined description $P_{t+1}$ that addresses the identified issues:
$$
P_{t+1} = \text{VLM}_{\text{critic}}(I_t, S, C, P_t)
$$
This revised description is then fed back to the Visualizer for regeneration. The Visualizer-Critic loop iterates for $T=3$ rounds, with the final output being $I = I_T$. This iterative refinement process ensures that the final illustration meets the high standards required for academic dissemination.

### Extension to Statistical Plots

The framework extends to statistical plots by adjusting the Visualizer and Critic agents. For numerical precision, the Visualizer converts the description $P_t$ into executable Python Matplotlib code: $I_t = \text{VLM}_{\text{code}}(P_t)$. The Critic evaluates the rendered plot and generates a refined description $P_{t+1}$ addressing inaccuracies or imperfections: $P_{t+1} = \text{VLM}_{\text{critic}}(I_t, S, C, P_t)$. The same $T=3$ round iterative refinement process applies. While we prioritize this code-based approach for accuracy, we also explore direct image generation in Section \ref{sec:discussion}. See Appendix \ref{app_sec:plot_agent_prompt} for adjusted prompts.""",
        "caption": "Figure 1: Overview of our PaperVizAgent framework. Given the source context and communicative intent, we first apply a Linear Planning Phase to retrieve relevant reference examples and synthesize a stylistically optimized description. We then use an Iterative Refinement Loop (consisting of Visualizer and Critic agents) to transform the description into visual output and conduct multi-round refinements to produce the final academic illustration.",
    },

    "Transformer Architecture": {
        "method": r"""## The Transformer Architecture

We propose a novel sequence-to-sequence model based entirely on attention mechanisms, dispensing with recurrence and convolutions. The Transformer follows an encoder-decoder structure, where both the encoder and decoder are composed of stacked layers.

### Encoder

The encoder consists of a stack of $N=6$ identical layers. Each layer has two sub-layers: (1) a multi-head self-attention mechanism, and (2) a position-wise fully connected feed-forward network. We employ a residual connection around each sub-layer, followed by layer normalization. That is, the output of each sub-layer is $\text{LayerNorm}(x + \text{Sublayer}(x))$.

### Multi-Head Attention

Instead of performing a single attention function, we linearly project the queries, keys and values $h=8$ times with different learned linear projections. On each of these projected versions, we perform the scaled dot-product attention in parallel:
$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$
The outputs are concatenated and projected again:
$$
\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h)W^O
$$

### Decoder

The decoder also consists of $N=6$ identical layers. In addition to the two sub-layers in the encoder, the decoder inserts a third sub-layer that performs multi-head cross-attention over the encoder output. The self-attention in the decoder is masked to prevent positions from attending to subsequent positions, ensuring autoregressive generation.

### Positional Encoding

Since the model contains no recurrence or convolution, we inject positional information using sinusoidal functions:
$$
PE_{(pos, 2i)} = \sin(pos / 10000^{2i/d_{\text{model}}})
$$
$$
PE_{(pos, 2i+1)} = \cos(pos / 10000^{2i/d_{\text{model}}})
$$

### Feed-Forward Network

Each layer contains a fully connected feed-forward network applied to each position separately and identically:
$$
\text{FFN}(x) = \max(0, xW_1 + b_1)W_2 + b_2
$$
The inner layer has dimensionality $d_{ff}=2048$, while the input and output dimensionality is $d_{\text{model}}=512$.""",
        "caption": "Figure 1: The Transformer model architecture. The encoder (left) maps an input sequence to a sequence of continuous representations, while the decoder (right) generates an output sequence one element at a time in an autoregressive fashion. Both stacks consist of multi-head self-attention and feed-forward sub-layers with residual connections and layer normalization.",
    },

    "RAG Pipeline": {
        "method": r"""## Retrieval-Augmented Generation (RAG) Pipeline

We propose a Retrieval-Augmented Generation (RAG) system that enhances large language model outputs by grounding them in external knowledge retrieved at inference time.

### Document Processing & Indexing

The pipeline begins with a Document Processing stage where raw documents (PDFs, web pages, databases) are ingested and split into chunks of approximately 512 tokens with 50-token overlap. Each chunk $c_i$ is embedded into a dense vector $\mathbf{e}_i \in \mathbb{R}^{768}$ using a pre-trained embedding model (e.g., text-embedding-3-large). These embeddings are stored in a vector database (e.g., FAISS, Pinecone) along with metadata for efficient similarity search.

### Query Processing

When a user submits a query $q$, it first passes through a Query Rewriter module that reformulates the query for better retrieval:
$$
q' = \text{LLM}_{\text{rewrite}}(q, \text{history})
$$
The rewritten query $q'$ is then embedded using the same embedding model: $\mathbf{e}_q = \text{Embed}(q')$.

### Retrieval

The retriever performs approximate nearest neighbor search over the vector index to find the top-$k$ most relevant chunks:
$$
\mathcal{C}_k = \text{top-}k\left(\{\text{sim}(\mathbf{e}_q, \mathbf{e}_i) \mid c_i \in \mathcal{D}\}\right)
$$
where $\text{sim}(\cdot, \cdot)$ denotes cosine similarity. We use $k=5$ in our experiments.

### Context Assembly & Generation

The retrieved chunks $\mathcal{C}_k$ are assembled into a context window along with the original query. A Re-Ranker module scores and reorders the chunks by relevance before they are passed to the generator LLM:
$$
\text{response} = \text{LLM}_{\text{gen}}(q, \text{Re-Rank}(\mathcal{C}_k))
$$

### Post-Processing & Citation

The generated response undergoes a Citation Verification step where each claim is traced back to source chunks, and inline citations are inserted. A Hallucination Detector cross-checks the response against retrieved evidence to flag unsupported statements.""",
        "caption": "Figure 1: Overview of our Retrieval-Augmented Generation (RAG) pipeline. Documents are processed, chunked, and embedded into a vector store during the offline indexing phase. At inference time, user queries are rewritten, embedded, and used to retrieve relevant chunks via similarity search. Retrieved context is re-ranked and fed to the LLM for grounded response generation with citation verification.",
    },

    "Training Pipeline (Encoder-Decoder)": {
        "method": r"""## Training Pipeline for Encoder-Decoder Models

We present a comprehensive training pipeline for encoder-decoder models that spans three major phases: data preparation, model training, and evaluation with deployment.

### Phase 1: Data Preparation

Raw data from multiple sources (web crawls, parallel corpora, domain-specific datasets) is collected and undergoes preprocessing. The preprocessing pipeline includes: (1) deduplication using MinHash locality-sensitive hashing, (2) quality filtering via a trained classifier that removes low-quality samples, (3) tokenization using SentencePiece with a vocabulary of 32,000 subword units, and (4) dynamic batching by sequence length to maximize GPU utilization.

The processed data is split into training (95\%), validation (2.5\%), and test (2.5\%) sets with stratified sampling to ensure domain coverage.

### Phase 2: Model Training

Training proceeds in two stages:

**Pre-training:** The encoder-decoder model is pre-trained on the full dataset using a denoising objective. We corrupt input sequences by randomly masking 15\% of tokens and train the model to reconstruct the original:
$$
\mathcal{L}_{\text{pretrain}} = -\sum_{t} \log P(x_t | x_{\backslash t}; \theta)
$$
We use AdamW optimizer with a learning rate schedule: linear warmup for 10,000 steps to $lr=3\times10^{-4}$, followed by cosine decay. Training is distributed across 64 TPU v4 chips using data parallelism with gradient accumulation.

**Fine-tuning:** The pre-trained model is fine-tuned on task-specific data using supervised learning. We apply LoRA (Low-Rank Adaptation) with rank $r=16$ to reduce trainable parameters:
$$
W' = W + \alpha \cdot BA, \quad B \in \mathbb{R}^{d \times r}, A \in \mathbb{R}^{r \times d}
$$

### Phase 3: Evaluation & Deployment

The trained model is evaluated on held-out test sets using task-specific metrics (BLEU, ROUGE, accuracy). We perform checkpoint selection based on validation performance across multiple checkpoints. The best checkpoint undergoes quantization (INT8) and is exported to an optimized serving format. The model is deployed behind a load balancer with auto-scaling, with A/B testing infrastructure to compare against baseline models.""",
        "caption": "Figure 1: End-to-end training pipeline for encoder-decoder models. The pipeline consists of three phases: (1) Data Preparation with deduplication, quality filtering, tokenization, and batching; (2) Model Training with pre-training using denoising objectives followed by LoRA fine-tuning; and (3) Evaluation and Deployment with checkpoint selection, quantization, and auto-scaled serving.",
    },
}
