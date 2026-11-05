# Multimodal RAG para Soporte Técnico de Interfaces POS con LangGraph

Este repositorio contiene la implementación de un sistema de **RAG Multimodal Avanzado (Retrieval-Augmented Generation)** diseñado específicamente para resolver consultas sobre manuales técnicos de software (Puntos de Venta). El sistema es capaz de "ver" e interpretar capturas de pantalla de la interfaz de usuario, flujos visuales y texto técnico simultáneamente.


## 🚀 Características Clave
*   **Embeddings Multimodales Nativos:** Implementación de `qwen3-embedding:4b` y `Ministral3:8B` para unificar capturas de pantalla de la interfaz (UI) y texto descriptivo en un mismo espacio vectorial de 2048 dimensiones.
*   **Orquestación Agéntica:** Flujo de control robusto desarrollado con `LangGraph` y `LangChain` bajo el patrón *Corrective RAG (CRAG)*.
*   **Persistencia Vectorial:** Configuración optimizada utilizando `ChromaDB` (para desarrollo local rápido).

*	**Ingesta con Docling + ChromaDB + qwen3-embedding + Ministral3 en Ollama

---

## 🏗️ Arquitectura del Sistema

El proyecto está dividido en dos pipelines principales: el **Pipeline de Ingestión (ETL)** y el **Ciclo de Inferencia Agéntica**.

---

## 🧠 Explicación de los Nodos (LangGraph)

El grafo de control administra el estado de la conversación y la calidad de la información recuperada a través de cuatro nodos clave:

### 1. `retriever_agent` (Nodo de Recuperación)
*   **Función:** Recibe la consulta en texto plano del usuario (`state['query']`).
*   **Lógica:** Transforma la consulta en un vector y realiza una búsqueda de similitud de coseno en la base de datos vectorial.
*   **Output:** Recupera los top-K documentos más relevantes. Cada documento contiene el texto del manual y la ruta (o Base64) de la captura de pantalla de la interfaz correspondiente. Los guarda en `state['documents']`.

### 2. `visual_grader_agent` (Nodo Evaluador)
*   **Función:** Actúa como un filtro de calidad de tipo *Self-RAG*.
*   **Lógica:** Utiliza un Modelo qwen3-embedding. El modelo analiza la pregunta del usuario y evalúa si las imágenes de la interfaz y el texto recuperado por el nodo anterior realmente contienen la solución.
*   **Output:** Actualiza `state['is_relevant']` con un valor booleano (`True` / `False`). Funciona como el enrutador lógico (*conditional edge*) del grafo.

### 3. `generator_agent` (Nodo de Generación)
*   **Función:** Produce la respuesta final estructurada para el usuario final.
*   **Lógica:** Si el evaluador dio luz verde, este nodo toma la consulta, el texto técnico y la imagen de la UI. El VLM redacta una guía paso a paso (ej. *"Debes hacer clic en el botón '%' rojo ubicado abajo a la derecha, como se muestra en la imagen"*).
*   **Output:** Guarda la respuesta en `state['generation']` junto con la referencia visual.

### 4. `rewrite_agent` (Nodo de Reescritura)
*   **Función:** Recuperación correctiva si el contexto inicial fue irrelevante o insuficiente.
*   **Lógica:** Si el evaluador determina que los vectores recuperados no sirven, este nodo toma la pregunta original y la reformula semánticamente para optimizar una segunda búsqueda en la base de datos (evitando que el sistema alucine).
*   **Output:** Actualiza `state['query']` con la nueva versión y redirige el flujo de vuelta al `retriever_agent`.

---

## 🛠️ Stack Tecnológico Utilizado
*   **Frameworks de IA:** LangGraph, LangChain Community.
*   **Modelos de Embeddings y VLM:** qwen3-embedding y Ministral3.
*   **Bases de Datos:** ChromaDB.
*   **Lenguaje:** Python 3.11+