import re

MOCK_DATABASE = [
    {
        "title": "Deep Learning Models for Automated Cancer Classification in Histopathology",
        "authors": "Sarah Jenkins, Robert Chen, David Miller",
        "year": 2022,
        "id": "arXiv:2203.14921",
        "url": "https://www.semanticscholar.org/paper/Deep-Learning-Models-for-Automated-Cancer-Jenkins-Chen/220314921",
        "pdf": "https://arxiv.org/pdf/2203.14921.pdf",
        "citations": 128,
        "abstract": "We present a comprehensive evaluation of deep learning architectures for automated classification of cancerous cells in histopathology images. By utilizing transfer learning with convolutional neural networks (CNNs), we achieve a precision rate of 98.2% and recall of 96.5% on multi-class cancer datasets, demonstrating the high efficacy of deep models in clinical workflows."
    },
    {
        "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
        "authors": "Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin",
        "year": 2020,
        "id": "arXiv:2005.11401",
        "url": "https://www.semanticscholar.org/paper/Retrieval-Augmented-Generation-for-Knowledge-Intensive-Lewis-Perez/1f077637694c8cba149147e4f7a88d4c7c4bbd85",
        "pdf": "https://arxiv.org/pdf/2005.11401.pdf",
        "citations": 655,
        "abstract": "We propose Retrieval-Augmented Generation (RAG), a general-purpose fine-tuning recipe that combines pre-trained parametric and non-parametric memory for language generation. We show that RAG models produce more accurate, factual, and diverse responses on open-domain QA and knowledge-intensive tasks."
    },
    {
        "title": "Attention Is All You Need",
        "authors": "Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones",
        "year": 2017,
        "id": "arXiv:1706.03762",
        "url": "https://www.semanticscholar.org/paper/Attention-Is-All-You-Need-Vaswani-Shazeer/a1170603762",
        "pdf": "https://arxiv.org/pdf/1706.03762.pdf",
        "citations": 84200,
        "abstract": "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments show these models to be superior in quality while being more parallelizable."
    },
    {
        "title": "Unsupervised Anomalous Sound Detection for Machine Condition Monitoring",
        "authors": "Kenji Suzuki, Akira Tanaka, Takashi Sato",
        "year": 2021,
        "id": "arXiv:2104.09312",
        "url": "https://www.semanticscholar.org/paper/Unsupervised-Anomalous-Sound-Detection-Suzuki-Tanaka/b1210409312",
        "pdf": "https://arxiv.org/pdf/2104.09312.pdf",
        "citations": 76,
        "abstract": "We address the problem of detecting anomalous machine sounds under unsupervised conditions where only normal operating sounds are available during training. We present a novel autoencoder framework combined with self-supervised contrastive learning to extract robust acoustic representations, outperforming standard baseline models."
    },
    {
        "title": "Generative Adversarial Nets",
        "authors": "Ian Goodfellow, Jean Pouget-Abadie, Mehdi Mirza, Bing Xu",
        "year": 2014,
        "id": "arXiv:1406.2661",
        "url": "https://www.semanticscholar.org/paper/Generative-Adversarial-Nets-Goodfellow-Pouget-Abadie/14062661",
        "pdf": "https://arxiv.org/pdf/1406.2661.pdf",
        "citations": 58400,
        "abstract": "We propose a new framework for estimating generative models via an adversarial process, in which we simultaneously train two models: a generative model that captures the data distribution, and a discriminative model that estimates the probability that a sample came from the training data rather than the generative model."
    },
    {
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "authors": "Jacob Devlin, Ming-Wei Chang, Kenton Lee, Kristina Toutanova",
        "year": 2018,
        "id": "arXiv:1810.04805",
        "url": "https://www.semanticscholar.org/paper/BERT-Pre-training-of-Deep-Bidirectional-Transformers-Devlin-Chang/181004805",
        "pdf": "https://arxiv.org/pdf/1810.04805.pdf",
        "citations": 105200,
        "abstract": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers."
    },
    {
        "title": "Deep Residual Learning for Image Recognition",
        "authors": "Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun",
        "year": 2015,
        "id": "arXiv:1512.03385",
        "url": "https://www.semanticscholar.org/paper/Deep-Residual-Learning-for-Image-Recognition-He-Zhang/151203385",
        "pdf": "https://arxiv.org/pdf/1512.03385.pdf",
        "citations": 194000,
        "abstract": "Deeper neural networks are more difficult to train. We present a residual learning framework to ease the training of networks that are substantially deeper than those previously used. We explicitly reformulate the layers as learning residual functions with reference to the layer inputs, instead of learning unreferenced functions."
    },
    {
        "title": "Adam: A Method for Stochastic Optimization",
        "authors": "Diederik Kingma, Jimmy Ba",
        "year": 2014,
        "id": "arXiv:1412.6980",
        "url": "https://www.semanticscholar.org/paper/Adam-A-Method-for-Stochastic-Optimization-Kingma-Ba/14126980",
        "pdf": "https://arxiv.org/pdf/1412.6980.pdf",
        "citations": 168000,
        "abstract": "We introduce Adam, an algorithm for first-order gradient-based optimization of stochastic objective functions, based on adaptive estimates of lower-order moments. The method is straightforward to implement, is computationally efficient, has little memory requirement, and is well suited for problems that are large in terms of data and/or parameters."
    },
    {
        "title": "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
        "authors": "Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov, Dirk Weissenborn",
        "year": 2020,
        "id": "arXiv:2010.11929",
        "url": "https://www.semanticscholar.org/paper/An-Image-is-Worth-16x16-Words-Transformers-for-Image-Dosovitskiy-Beyer/201011929",
        "pdf": "https://arxiv.org/pdf/2010.11929.pdf",
        "citations": 28000,
        "abstract": "While the Transformer architecture has become the de facto standard for natural language processing tasks, its applications to computer vision remain limited. We show that this reliance on CNNs is not necessary and a pure Transformer applied directly to sequences of image patches can perform very well on image classification tasks."
    },
    {
        "title": "A Survey of Large Language Model Agents for Scientific Discovery",
        "authors": "Alice Johnson, Michael Chang, Emily Zhao",
        "year": 2023,
        "id": "arXiv:2308.10928",
        "url": "https://www.semanticscholar.org/paper/A-Survey-of-Large-Language-Model-Agents-for-Johnson-Chang/230810928",
        "pdf": "https://arxiv.org/pdf/2308.10928.pdf",
        "citations": 89,
        "abstract": "This survey provides a systematic review of large language model (LLM) agents configured for scientific workflows. We analyze different cognitive architectures (ReAct, Plan-and-Solve) and their application in automated literature synthesis, chemical formulation, and medical diagnostic coding."
    }
]


def _search_mock_database(query: str, limit: int = 3) -> list:
    query_words = re.findall(r"\w+", query.lower())
    scored_papers = []
    for paper in MOCK_DATABASE:
        score = 0
        text_to_search = (paper["title"] + " " + paper["abstract"]).lower()
        for word in query_words:
            if word in text_to_search:
                score += 1
        scored_papers.append((score, paper))

    scored_papers.sort(key=lambda x: x[0], reverse=True)
    matched = [paper for score, paper in scored_papers if score > 0]
    return matched[:limit]
