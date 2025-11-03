
# Análisis Funcional y Arquitectónico: "Broker Assistant"
## Aplicación Web de Asistencia en Inversiones Bursátiles (Flask/IA)

Este documento describe la funcionalidad y la arquitectura técnica de la aplicación web de asistencia en inversiones bursátiles, denominada provisionalmente "Broker Assistant". La plataforma utiliza un motor de Inteligencia Artificial (IA) para generar sugerencias de compra/venta basadas en dos pilares: el análisis de noticias (*Análisis Fundamental Cuantitativo*) y la interpretación de patrones en gráficos de velas (*Análisis Técnico Automatizado*).

La aplicación se construirá sobre el *framework* web **Flask** (Python), y su inteligencia central se alimentará de grandes modelos de lenguaje (LLMs) y modelos de *Machine Learning* (ML) como los proporcionados por **Claude**, **OpenAI** o **Deepseek**.

---

## I. Funcionalidades Clave de la Plataforma

La aplicación Broker Assistant se organiza en tres módulos principales orientados al usuario, complementados por un módulo de aprendizaje continuo en el *backend*.

### 1. Motor de Sugerencias de Inversión (IA)

El corazón de la aplicación es su motor de IA, que ofrece sugerencias de entrada (compra) y salida (venta) mediante dos metodologías:

#### A. Análisis Técnico Automatizado (Gráficos de Velas)
Este módulo se especializa en el reconocimiento de patrones bursátiles en tiempo real.

*   **Detección de Patrones:** Utiliza algoritmos de *Machine Learning* para escanear cientos de activos e identificar al instante formaciones complejas como "cabeza y hombros", "doble fondo" o "banderas alcistas", con una precisión que puede superar el 80%.
*   **Indicadores Clave:** Las sugerencias se apoyan en la integración de indicadores técnicos esenciales, incluyendo :
    *   **Bandas de Bollinger:** Para medir la volatilidad y detectar posibles reversiones.
    *   **Índice de Fuerza Relativa (RSI):** Para identificar condiciones de sobrecompra o sobreventa.
    *   **Oscilador Estocástico:** Para comparar el precio de cierre con el rango de negociación reciente, señalando extremos de mercado.
*   **Visualización Interactiva:** La interfaz debe presentar gráficos de velas interactivos de baja latencia. Para la visualización se pueden utilizar librerías de JavaScript como Highcharts (gratis para uso no comercial)  o Chart.js (código abierto).

#### B. Análisis de Noticias (Análisis Fundamental Cuantitativo)
Este módulo automatiza el análisis fundamental basado en la actualidad del mercado.

*   **Ingesta de Noticias:** Mediante APIs especializadas, la plataforma ingiere noticias bursátiles y datos fundamentales.
*   **Criterios Algorítmicos:** El motor de IA procesa la información y filtra activos basándose en la salud financiera. Los criterios típicos de filtrado fundamental que el algoritmo puede aplicar incluyen :
    *   Baja relación precio-ganancia (P/E).
    *   Precio menor que el valor contable de la empresa.
    *   Rendimiento de dividendos por encima del promedio (pero no excesivamente alto).

### 2. Gestión de Cartera y Datos del Usuario

La aplicación debe permitir a los usuarios gestionar y hacer un seguimiento de sus intereses y posiciones de inversión.

*   **Posiciones Abiertas (Seguimiento de Cartera):** Módulo para que el usuario registre y siga las operaciones de compra y venta realizadas. Esto se gestionará con una base de datos relacional de baja latencia (ej. PostgreSQL o MySQL) que forma parte de la arquitectura transaccional de la aplicación.
*   **Activos Favoritos:** Los usuarios pueden marcar activos de interés. Esta lista no solo mejora la experiencia de usuario (UX), sino que genera datos etiquetados de alto valor que alimentan los modelos de IA para personalizar las futuras sugerencias.

### 3. Aprendizaje Continuo y Backtesting (Histórico de Propuestas)

El desarrollo de la aplicación incorpora un mecanismo de aprendizaje continuo basado en el rendimiento de sus propias predicciones.

*   **Registro de Predicciones:** La aplicación debe guardar un **histórico de todas las sugerencias de entrada y salida** generadas por el motor de IA, independientemente de si el usuario las ejecutó. Este registro actúa como el "conjunto de entrenamiento" para la mejora del modelo.
*   **Modelos Híbridos (ARIMA-LSTM):** Para aprender de las series temporales y el histórico, el sistema utilizará modelos híbridos avanzados de *Machine Learning* (como ARIMA-LSTM) que combinan la detección de tendencias lineales con el reconocimiento de patrones no lineales a largo plazo, buscando mejorar la precisión en el pronóstico financiero.
*   **Transparencia (XAI):** Para generar confianza, las sugerencias deben ser justificadas por el sistema (IA Explicable), vinculando el pronóstico del ML a los factores técnicos o fundamentales que lo desencadenaron.

---

## II. Arquitectura Técnica (Flask y Backend)

La aplicación web, desarrollada en Flask, requerirá una infraestructura de *backend* robusta para manejar el volumen y la velocidad de los datos financieros.

El despliegue se realizara con docker

### 1. Servidor Web y Framework

| Componente | Tecnología | Propósito |
|---|---|---|
| **Framework Web** | **Flask** (Python) | Proporciona la estructura ligera y flexible para el desarrollo rápido de la API del *backend* y la lógica de negocio. |
| **Modelos de IA** | **Claude, OpenAI, Deepseek** | Utilizados para el procesamiento de lenguaje natural (NLP) en el análisis de noticias y para la generación de análisis de mercado avanzado a partir de datos estructurados. |

### 2. Infraestructura de Datos y Latencia

El pilar de la plataforma es la obtención de datos "actualizados y precisos en el momento adecuado".

*   **Streaming de Datos de Precios:** Para manejar el flujo constante de precios de la bolsa con baja latencia, la arquitectura recomendada es utilizar **Apache Kafka** en el *backend* como plataforma de mensajería distribuida. Esto asegura la integridad, durabilidad y alta escalabilidad de los datos.
*   **Distribución al Cliente:** Para llevar los precios en tiempo real al navegador del usuario, Kafka se integrará con **WebSockets**. Este enfoque proporciona un canal de comunicación bidireccional continuo, superando la lentitud de los métodos de actualización tradicionales (como *polling* o REST).
*   **Caché de Alto Rendimiento:** Para acelerar la carga de gráficos y reducir las llamadas a APIs de pago por uso, se implementará una capa de *caching* en memoria (ej. Redis). Esto permite la lectura de datos históricos a velocidades ultrarrápidas, a menudo en menos de un milisegundo.

### 3. Seguridad de Datos

La información del usuario, especialmente las "Posiciones Abiertas", se considera información sensible.

*   **Cifrado de Datos en Reposo (*Data at Rest*):** Los datos almacenados en la base de datos (posiciones, histórico) se protegerán con cifrado **AES-256** para prevenir accesos no autorizados en caso de robo de la base de datos.
*   **Cifrado en Tránsito (*Data in Transit*):** La transmisión de datos a través de la red (WebSockets, API) debe estar protegida con protocolos seguros como **TLS/SSL o HTTPS**, que utilizan claves dinámicas.
