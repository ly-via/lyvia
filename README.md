# Stock Volatility Analysis
This project explores predictive modeling techniques to forecast stock market volatility, aiming to identify the most suitable model for capturing market dynamics across various sectors.

## Project Overview
Volatility forecasting is a critical aspect of financial risk management. This project applies and compares multiple time series models to predict volatility in ASX-listed stock prices, helping to uncover the best-suited approach for accurate and timely forecasting.

## Objectives
- **Model Comparison**: Evaluate and compare the performance of multiple volatility forecasting models.
- **Feature Engineering**: Derive features such as daily returns and realized volatility for model input.
- **Model Selection**: Identify the most effective model in terms of prediction accuracy and robustness.

## Approach
- **Data Preparation**: Collected and cleaned historical stock price data, calculated daily returns and realised volatility.
- **Model Implementation**: Built and tuned several volatility models, including:
-   HAR (Heterogeneous AutoRegressive)
-   LM (Linear Model)
-   HAV (High-frequency-based Volatility models)
- **Evaluation**: Assessed model performance using statistical metrics such as RMSE and out-of-sample forecasting accuracy.
- **Insight Generation**: Analysed which models best captured volatility dynamics under different market conditions.

## Tools and Technologies
- **R**: For data cleaning, preprocessing, models building and evaluation metrics.
  
## Results
The HAR model demonstrated superior predictive performance in capturing multi-scale volatility patterns, while the simpler LM model provided faster computation with trade-offs in accuracy. These findings highlight model-specific strengths in different forecasting contexts, offering guidance for future use in financial decision-making and risk management.
