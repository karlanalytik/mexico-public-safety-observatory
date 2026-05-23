# Mexico Public Safety Observatory

## Project Description

**Mexico Public Safety Observatory** is an interactive data product that transforms official public crime records from Mexico into an accessible violence intelligence platform for citizens, researchers, and decision-makers.

The solution processes over ten years of public crime data at the state level, combines it with population estimates, and applies unsupervised machine learning techniques to generate a normalized violence index for each Mexican state. The final product is an interactive web application that allows users to explore the current public safety landscape, compare states, and analyze historical trends through intuitive visualizations.

## Objective

The objective of this project is to make complex public safety data easier to understand and more actionable by converting fragmented official records into a single interpretable metric.

Instead of relying on arbitrary weighting schemes, the solution uses **Principal Component Analysis (PCA)** to derive a data-driven violence score and **K-means clustering** to classify states into violence risk levels **(Low, Medium, High, Critical)**. This enables users to quickly understand how violence evolves across Mexico using transparent, data-based insights.

## Interactive Application

The final product is an interactive web application designed to make public safety data easy to explore and understand.

Users can visualize Mexico’s violence index through an interactive map, compare states in a national ranking, analyze historical trends, and review state-level summaries in just a few clicks—without needing any technical knowledge or direct access to the underlying data infrastructure.

Explore the application here: [Observatorio de Seguridad Pública en México](http://violence-observ-alb-1499440888.us-east-1.elb.amazonaws.com)


## Repository Structure

```
.
├── docs
│   ├── 01_Definicion_del_Producto.pdf
│   ├── 02_FAQ_del_Producto.pdf
│   └── 03_Arquitectura_de_la_solucion.pdf
├── glue
│   └── etl_delitos.py
├── LICENSE
├── README.md
├── run_pipeline.py
├── sagemaker
│   ├── 01_pca_kmeans.ipynb
│   └── pca_kmeans.py
└── streamlit
    ├── ecs-fargate-app.yaml
    └── violence-observatory
        ├── backend
        ├── data
        │   └── estados-poligonos.geojson
        ├── Dockerfile
        ├── environment.yml
        └── frontend
            ├── app.py
            ├── __init__.py
            └── src
                └── data.py
```

## Project Structure

- **Data Processing (`glue/`, `run_pipeline.py`)**  
  ETL scripts and pipeline orchestration for cleaning, transforming, and preparing the raw public safety datasets.

- **Data Modeling (`sagemaker/`)**  
  PCA and K-means modeling code used to generate the violence index and state-level risk classification.

- **Interactive Application (`streamlit/`)**  
  Streamlit web application, Docker configuration, and AWS ECS Fargate deployment template for serving the final product.

- **Documentation (`docs/`)**  
  Supporting project documentation, including product definition, FAQ, and solution architecture.


## Use of AI Tools in the Project

AI tools were used as a support resource throughout the development of this project, primarily to improve efficiency in documentation and communication tasks, as well as to assist in resolving specific technical questions.

Their use included:

- Generating and refining documentation for functions and scripts.
Translating and synthesizing sections of the README (e.g., Project Objective and Description) based on the report content.
- Reviewing and improving English writing, particularly for logging messages and technical descriptions, to ensure clarity and natural language usage.
- Assisting with specific technical questions, such as configuring access roles, ...

All architectural decisions, system design, implementation, and validation of the solution were carried out by us.