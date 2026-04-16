# 🍰 SweetBalance AI

Sistema inteligente de recomendación de postres que integra inteligencia artificial, costo y perfil nutricional para apoyar la toma de decisiones.

---

## 📌 Descripción del proyecto

SweetBalance AI es una aplicación desarrollada como parte de un diplomado en ciencia de datos, cuyo objetivo es recomendar recetas de postres personalizadas considerando:

* Preferencias del usuario
* Costo de preparación (datos PROFECO)
* Información nutricional
* Restricciones alimentarias

El sistema busca transformar la elección de un postre en una decisión informada, accesible y adaptada al usuario.

---

## 🎯 Objetivo

Desarrollar un sistema de recomendación de postres que combine técnicas de inteligencia artificial con datos de costo y nutrición, permitiendo sugerencias relevantes y personalizadas.

---

## 🧠 Enfoque del modelo

El sistema se basa en un enfoque de similitud utilizando embeddings generados con OpenAI.

Se construyeron dos tipos de embeddings:

* 🔹 **Ingredientes + sustituciones**
* 🔹 **Nombre + instrucciones**

El modelo de recomendación (`cuisine_similarity`) se definió como:

* 70% similitud en ingredientes + sustituciones
* 30% similitud en nombre + instrucciones

Esto permite capturar tanto la composición como el contexto de las recetas.

---

## 📊 Fuentes de datos

* **Spoonacular API**

  * Recetas
  * Ingredientes
  * Información nutricional

* **PROFECO (México)**

  * Precios de ingredientes (segunda quincena de febrero)

---

## 🧹 Procesamiento y limpieza de datos

Se aplicaron procesos de ingeniería de datos para garantizar calidad y consistencia:

* Identificación de tipos de variables
* Eliminación de duplicados
* Tratamiento de valores nulos
* Estandarización de ingredientes mediante OpenAI
* Normalización de variables textuales y numéricas

---

## 🤖 Uso de inteligencia artificial

Se utilizó OpenAI para:

* Generación de embeddings
* Estandarización de ingredientes
* Generación de perfiles nutricionales
* Recomendaciones y alternativas de ingredientes
* Identificación de precauciones para usuarios con condiciones específicas

---

## ⚙️ Funcionalidades del sistema

* 🔍 Búsqueda de recetas
* 🍰 Recomendación de postres personalizados
* 🥗 Perfil nutricional interpretado
* ♻️ Sustitución de ingredientes
* ⚖️ Estimación de costo
* 🌱 Filtros (vegano, vegetariano, número de ingredientes)

---

## 💻 Tecnologías utilizadas

* Python
* Streamlit
* OpenAI API
* Pandas / NumPy
* APIs externas (Spoonacular)

---

## 🌐 Aplicación

👉 [Acceder a la app](https://sweetbalanceai-ds.streamlit.app/)

---

## 💡 Propuesta de valor

SweetBalance AI combina:

* Inteligencia artificial
* Costo real
* Personalización

Para ofrecer recomendaciones accesibles y relevantes.

---

## 🚀 Modelo de negocio (propuesto)

* Freemium (funcionalidades básicas)
* Suscripción premium (filtros avanzados y personalización)
* Afiliación con supermercados (compra de ingredientes)

---

## 🔮 Próximos pasos

* Desarrollo de aplicación móvil
* Personalización por usuario
* Integración con plataformas de compra

---

## 👩‍💻 Autora

**Emma Martínez**
Diplomado en Ciencia de Datos

---

## 📄 Licencia

Este proyecto es de carácter académico.

