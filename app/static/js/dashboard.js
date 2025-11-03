// Global state
let currentSymbol = 'AAPL';
let socket = null;
let chart = null;
let historicalData = [];

// Initialize WebSocket connection
function initWebSocket() {
    socket = io('http://localhost:5000', {
        transports: ['websocket', 'polling']
    });

    socket.on('connect', () => {
        console.log('WebSocket connected');
        updateConnectionStatus(true);
    });

    socket.on('disconnect', () => {
        console.log('WebSocket disconnected');
        updateConnectionStatus(false);
    });

    socket.on('price_update', (data) => {
        console.log('Price update:', data);
        updatePriceDisplay(data);
    });

    socket.on('portfolio_update', (data) => {
        console.log('Portfolio update:', data);
        updatePortfolioDisplay(data);
    });
}

function updateConnectionStatus(connected) {
    const indicator = document.querySelector('.status-indicator');
    if (connected) {
        indicator.style.background = '#3fb950';
    } else {
        indicator.style.background = '#f85149';
    }
}

// Generate realistic historical price data
function generateHistoricalData(symbol, days = 100) {
    const data = [];
    const basePrice = {
        'AAPL': 180,
        'TSLA': 250,
        'MSFT': 380,
        'GOOGL': 140,
        'AMZN': 170
    }[symbol] || 100;

    let price = basePrice;
    const now = Date.now();
    const dayMs = 24 * 60 * 60 * 1000;

    for (let i = days; i >= 0; i--) {
        const timestamp = now - (i * dayMs);
        const change = (Math.random() - 0.48) * (price * 0.03);
        price = price + change;

        const open = price;
        const close = price + (Math.random() - 0.5) * (price * 0.02);
        const high = Math.max(open, close) + Math.random() * (price * 0.01);
        const low = Math.min(open, close) - Math.random() * (price * 0.01);
        const volume = Math.floor(Math.random() * 10000000) + 5000000;

        data.push({
            timestamp: new Date(timestamp).toISOString(),
            open: parseFloat(open.toFixed(2)),
            high: parseFloat(high.toFixed(2)),
            low: parseFloat(low.toFixed(2)),
            close: parseFloat(close.toFixed(2)),
            volume: volume
        });
    }

    return data;
}

// Initialize chart
function initChart() {
    const chartData = historicalData.map(d => [
        new Date(d.timestamp).getTime(),
        d.open,
        d.high,
        d.low,
        d.close
    ]);

    const volumeData = historicalData.map(d => [
        new Date(d.timestamp).getTime(),
        d.volume
    ]);

    chart = Highcharts.stockChart('main-chart', {
        chart: {
            backgroundColor: '#0d1117',
            style: {
                fontFamily: 'Segoe UI, sans-serif'
            }
        },
        rangeSelector: {
            selected: 1,
            buttonTheme: {
                fill: '#1c2128',
                stroke: '#30363d',
                style: {
                    color: '#e6edf3'
                },
                states: {
                    hover: {
                        fill: '#30363d',
                        style: {
                            color: '#e6edf3'
                        }
                    },
                    select: {
                        fill: '#58a6ff',
                        style: {
                            color: '#ffffff'
                        }
                    }
                }
            },
            inputStyle: {
                color: '#e6edf3',
                backgroundColor: '#1c2128'
            },
            labelStyle: {
                color: '#8b949e'
            }
        },
        title: {
            text: `${currentSymbol} - Análisis Técnico`,
            style: {
                color: '#e6edf3'
            }
        },
        xAxis: {
            lineColor: '#30363d',
            tickColor: '#30363d',
            labels: {
                style: {
                    color: '#8b949e'
                }
            }
        },
        yAxis: [{
            labels: {
                align: 'right',
                x: -3,
                style: {
                    color: '#8b949e'
                }
            },
            title: {
                text: 'Precio',
                style: {
                    color: '#e6edf3'
                }
            },
            height: '70%',
            lineWidth: 2,
            gridLineColor: '#30363d',
            resize: {
                enabled: true
            }
        }, {
            labels: {
                align: 'right',
                x: -3,
                style: {
                    color: '#8b949e'
                }
            },
            title: {
                text: 'Volumen',
                style: {
                    color: '#e6edf3'
                }
            },
            top: '75%',
            height: '25%',
            offset: 0,
            lineWidth: 2,
            gridLineColor: '#30363d'
        }],
        tooltip: {
            backgroundColor: '#1c2128',
            borderColor: '#30363d',
            style: {
                color: '#e6edf3'
            },
            split: true
        },
        plotOptions: {
            candlestick: {
                color: '#f85149',
                upColor: '#3fb950',
                lineColor: '#f85149',
                upLineColor: '#3fb950'
            }
        },
        series: [{
            type: 'candlestick',
            name: currentSymbol,
            data: chartData,
            id: 'main-series',
            tooltip: {
                valueDecimals: 2
            }
        }, {
            type: 'column',
            name: 'Volumen',
            data: volumeData,
            yAxis: 1,
            color: '#58a6ff'
        }],
        credits: {
            enabled: false
        },
        navigator: {
            maskFill: 'rgba(88, 166, 255, 0.1)',
            outlineColor: '#30363d',
            xAxis: {
                gridLineColor: '#30363d'
            }
        },
        scrollbar: {
            barBackgroundColor: '#30363d',
            barBorderColor: '#30363d',
            buttonBackgroundColor: '#30363d',
            buttonBorderColor: '#30363d',
            rifleColor: '#8b949e',
            trackBackgroundColor: '#1c2128',
            trackBorderColor: '#30363d'
        }
    });

    // Add indicators to chart
    chart.addSeries({
        type: 'sma',
        linkedTo: 'main-series',
        params: {
            period: 20
        },
        marker: {
            enabled: false
        },
        color: '#58a6ff',
        name: 'SMA (20)'
    });

    chart.addSeries({
        type: 'sma',
        linkedTo: 'main-series',
        params: {
            period: 50
        },
        marker: {
            enabled: false
        },
        color: '#f778ba',
        name: 'SMA (50)'
    });
}

// Analyze symbol
async function analyzeSymbol() {
    const symbol = document.getElementById('symbol-search').value.toUpperCase();
    if (!symbol) return;

    currentSymbol = symbol;
    showLoading();

    try {
        // Generate historical data
        historicalData = generateHistoricalData(symbol);

        // Get technical analysis
        const technicalData = await fetch('/api/analysis/technical/' + symbol, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ price_data: historicalData })
        }).then(r => r.json());

        console.log('Technical Analysis:', technicalData);

        // Get AI prediction
        const predictionData = await fetch('/api/analysis/predict/' + symbol, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ price_data: historicalData })
        }).then(r => r.json());

        console.log('AI Prediction:', predictionData);

        // Update UI
        updateChart();
        updateIndicators(technicalData.analysis);
        updateSuggestions(predictionData);

        // Subscribe to real-time updates
        if (socket && socket.connected) {
            socket.emit('subscribe_symbol', { symbol: symbol });
        }

    } catch (error) {
        console.error('Error analyzing symbol:', error);
        showError('Error al analizar el símbolo. Por favor intenta de nuevo.');
    }
}

function showLoading() {
    document.getElementById('suggestions-container').innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p style="margin-top: 15px;">Analizando ${currentSymbol}...</p>
        </div>
    `;
}

function showError(message) {
    document.getElementById('suggestions-container').innerHTML = `
        <div style="text-align: center; padding: 20px; color: #f85149;">
            <i class="fas fa-exclamation-triangle" style="font-size: 40px; margin-bottom: 10px;"></i>
            <p>${message}</p>
        </div>
    `;
}

function updateChart() {
    if (chart) {
        chart.destroy();
    }
    initChart();
}

function updateIndicators(analysis) {
    const indicators = analysis.indicators;

    // RSI
    if (indicators.rsi.value !== null) {
        document.getElementById('rsi-value').textContent = indicators.rsi.value.toFixed(2);
        document.getElementById('rsi-signal').textContent = indicators.rsi.signal;
        document.getElementById('rsi-signal').className = `indicator-signal signal-${indicators.rsi.signal.toLowerCase()}`;
    }

    // MACD
    if (indicators.macd.macd !== null) {
        document.getElementById('macd-value').textContent = indicators.macd.macd.toFixed(2);
        document.getElementById('macd-signal').textContent = indicators.macd.trend;
        document.getElementById('macd-signal').className = `indicator-signal signal-${indicators.macd.trend.toLowerCase()}`;
    }

    // Bollinger Bands
    if (indicators.bollinger_bands.current_price !== null) {
        document.getElementById('bb-value').textContent = '$' + indicators.bollinger_bands.current_price.toFixed(2);
        document.getElementById('bb-signal').textContent = indicators.bollinger_bands.signal;
        document.getElementById('bb-signal').className = `indicator-signal signal-${indicators.bollinger_bands.signal.toLowerCase()}`;
    }

    // Stochastic
    if (indicators.stochastic.k !== null) {
        document.getElementById('stoch-value').textContent = indicators.stochastic.k.toFixed(2);
        document.getElementById('stoch-signal').textContent = indicators.stochastic.signal;
        document.getElementById('stoch-signal').className = `indicator-signal signal-${indicators.stochastic.signal.toLowerCase()}`;
    }

    // Update detailed indicators view
    updateDetailedIndicators(indicators);
}

function updateDetailedIndicators(indicators) {
    const container = document.getElementById('indicators-detail');

    let html = '<h3 style="margin-bottom: 20px; color: #58a6ff;">Análisis Detallado de Indicadores</h3>';

    // RSI Section
    html += `
        <div style="background: #0d1117; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #30363d;">
            <h4 style="color: #58a6ff; margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                <i class="fas fa-chart-line"></i> RSI (Relative Strength Index)
            </h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                <div>
                    <div style="color: #8b949e; font-size: 12px; margin-bottom: 5px;">VALOR ACTUAL</div>
                    <div style="font-size: 32px; font-weight: 700;">${indicators.rsi.value !== null ? indicators.rsi.value.toFixed(2) : '--'}</div>
                </div>
                <div>
                    <div style="color: #8b949e; font-size: 12px; margin-bottom: 5px;">SEÑAL</div>
                    <div style="font-size: 24px; font-weight: 700; color: ${getSignalColor(indicators.rsi.signal)};">
                        ${indicators.rsi.signal.toUpperCase()}
                    </div>
                </div>
            </div>
            <div style="background: #1c2128; padding: 15px; border-radius: 6px;">
                <div style="font-size: 13px; color: #e6edf3; margin-bottom: 10px;">
                    <strong>Interpretación:</strong>
                </div>
                <div style="font-size: 13px; color: #8b949e; line-height: 1.6;">
                    ${getRSIInterpretation(indicators.rsi.value)}
                </div>
                <div style="margin-top: 15px; background: #0d1117; border-radius: 4px; height: 8px; position: relative; overflow: hidden;">
                    <div style="position: absolute; left: 0; width: 30%; height: 100%; background: linear-gradient(90deg, #f85149, #ff8c69);"></div>
                    <div style="position: absolute; left: 30%; width: 40%; height: 100%; background: #30363d;"></div>
                    <div style="position: absolute; left: 70%; width: 30%; height: 100%; background: linear-gradient(90deg, #56d364, #3fb950);"></div>
                    <div style="position: absolute; left: ${indicators.rsi.value}%; width: 3px; height: 100%; background: white; box-shadow: 0 0 8px white;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 11px; color: #8b949e;">
                    <span>Sobreventa (0-30)</span>
                    <span>Neutral (30-70)</span>
                    <span>Sobrecompra (70-100)</span>
                </div>
            </div>
        </div>
    `;

    // MACD Section
    html += `
        <div style="background: #0d1117; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #30363d;">
            <h4 style="color: #58a6ff; margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                <i class="fas fa-wave-square"></i> MACD (Moving Average Convergence Divergence)
            </h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                <div>
                    <div style="color: #8b949e; font-size: 12px; margin-bottom: 5px;">MACD</div>
                    <div style="font-size: 24px; font-weight: 700;">${indicators.macd.macd !== null ? indicators.macd.macd.toFixed(4) : '--'}</div>
                </div>
                <div>
                    <div style="color: #8b949e; font-size: 12px; margin-bottom: 5px;">SIGNAL</div>
                    <div style="font-size: 24px; font-weight: 700;">${indicators.macd.signal !== null ? indicators.macd.signal.toFixed(4) : '--'}</div>
                </div>
                <div>
                    <div style="color: #8b949e; font-size: 12px; margin-bottom: 5px;">HISTOGRAM</div>
                    <div style="font-size: 24px; font-weight: 700; color: ${indicators.macd.histogram >= 0 ? '#3fb950' : '#f85149'};">
                        ${indicators.macd.histogram !== null ? indicators.macd.histogram.toFixed(4) : '--'}
                    </div>
                </div>
            </div>
            <div style="background: #1c2128; padding: 15px; border-radius: 6px;">
                <div style="font-size: 13px; color: #e6edf3; margin-bottom: 10px;">
                    <strong>Tendencia:</strong> <span style="color: ${indicators.macd.trend === 'bullish' ? '#3fb950' : '#f85149'}; font-weight: 600;">
                        ${indicators.macd.trend === 'bullish' ? 'ALCISTA' : indicators.macd.trend === 'bearish' ? 'BAJISTA' : 'NEUTRAL'}
                    </span>
                </div>
                <div style="font-size: 13px; color: #8b949e; line-height: 1.6;">
                    ${getMACDInterpretation(indicators.macd)}
                </div>
            </div>
        </div>
    `;

    // Bollinger Bands Section
    html += `
        <div style="background: #0d1117; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #30363d;">
            <h4 style="color: #58a6ff; margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                <i class="fas fa-arrows-up-down"></i> Bandas de Bollinger
            </h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                <div>
                    <div style="color: #8b949e; font-size: 12px; margin-bottom: 5px;">BANDA SUPERIOR</div>
                    <div style="font-size: 20px; font-weight: 700;">$${indicators.bollinger_bands.upper !== null ? indicators.bollinger_bands.upper.toFixed(2) : '--'}</div>
                </div>
                <div>
                    <div style="color: #8b949e; font-size: 12px; margin-bottom: 5px;">MEDIA</div>
                    <div style="font-size: 20px; font-weight: 700;">$${indicators.bollinger_bands.middle !== null ? indicators.bollinger_bands.middle.toFixed(2) : '--'}</div>
                </div>
                <div>
                    <div style="color: #8b949e; font-size: 12px; margin-bottom: 5px;">BANDA INFERIOR</div>
                    <div style="font-size: 20px; font-weight: 700;">$${indicators.bollinger_bands.lower !== null ? indicators.bollinger_bands.lower.toFixed(2) : '--'}</div>
                </div>
            </div>
            <div style="background: #1c2128; padding: 15px; border-radius: 6px;">
                <div style="font-size: 13px; color: #e6edf3; margin-bottom: 10px;">
                    <strong>Precio Actual:</strong> $${indicators.bollinger_bands.current_price.toFixed(2)}
                </div>
                <div style="font-size: 13px; color: #8b949e; line-height: 1.6;">
                    ${getBollingerInterpretation(indicators.bollinger_bands)}
                </div>
                <div style="margin-top: 15px; position: relative; height: 60px; background: linear-gradient(180deg, #1c2128 0%, #0d1117 50%, #1c2128 100%);">
                    <div style="position: absolute; top: 0; left: 0; right: 0; height: 2px; background: #f85149;"></div>
                    <div style="position: absolute; top: 50%; left: 0; right: 0; height: 2px; background: #58a6ff; transform: translateY(-50%);"></div>
                    <div style="position: absolute; bottom: 0; left: 0; right: 0; height: 2px; background: #3fb950;"></div>
                    ${getBollingerPriceMarker(indicators.bollinger_bands)}
                </div>
            </div>
        </div>
    `;

    // Stochastic Section
    html += `
        <div style="background: #0d1117; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #30363d;">
            <h4 style="color: #58a6ff; margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                <i class="fas fa-signal"></i> Oscilador Estocástico
            </h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                <div>
                    <div style="color: #8b949e; font-size: 12px; margin-bottom: 5px;">%K (Rápido)</div>
                    <div style="font-size: 32px; font-weight: 700;">${indicators.stochastic.k !== null ? indicators.stochastic.k.toFixed(2) : '--'}</div>
                </div>
                <div>
                    <div style="color: #8b949e; font-size: 12px; margin-bottom: 5px;">%D (Lento)</div>
                    <div style="font-size: 32px; font-weight: 700;">${indicators.stochastic.d !== null ? indicators.stochastic.d.toFixed(2) : '--'}</div>
                </div>
            </div>
            <div style="background: #1c2128; padding: 15px; border-radius: 6px;">
                <div style="font-size: 13px; color: #e6edf3; margin-bottom: 10px;">
                    <strong>Señal:</strong> <span style="color: ${getSignalColor(indicators.stochastic.signal)}; font-weight: 600;">
                        ${indicators.stochastic.signal.toUpperCase().replace('_', ' ')}
                    </span>
                </div>
                <div style="font-size: 13px; color: #8b949e; line-height: 1.6;">
                    ${getStochasticInterpretation(indicators.stochastic)}
                </div>
                <div style="margin-top: 15px; background: #0d1117; border-radius: 4px; height: 8px; position: relative; overflow: hidden;">
                    <div style="position: absolute; left: 0; width: 20%; height: 100%; background: linear-gradient(90deg, #f85149, #ff8c69);"></div>
                    <div style="position: absolute; left: 20%; width: 60%; height: 100%; background: #30363d;"></div>
                    <div style="position: absolute; left: 80%; width: 20%; height: 100%; background: linear-gradient(90deg, #56d364, #3fb950);"></div>
                    <div style="position: absolute; left: ${indicators.stochastic.k}%; width: 3px; height: 100%; background: #58a6ff; box-shadow: 0 0 8px #58a6ff;"></div>
                    <div style="position: absolute; left: ${indicators.stochastic.d}%; width: 3px; height: 100%; background: #f778ba; box-shadow: 0 0 8px #f778ba;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 11px; color: #8b949e;">
                    <span>Sobreventa (0-20)</span>
                    <span>Neutral (20-80)</span>
                    <span>Sobrecompra (80-100)</span>
                </div>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

function getSignalColor(signal) {
    if (signal === 'buy' || signal === 'bullish') return '#3fb950';
    if (signal === 'sell' || signal === 'bearish') return '#f85149';
    return '#8b949e';
}

function getRSIInterpretation(rsiValue) {
    if (rsiValue === null) return 'No hay datos suficientes para calcular el RSI.';
    if (rsiValue < 30) return 'El RSI está en zona de sobreventa, indicando una posible oportunidad de compra. El activo podría estar infravalorado.';
    if (rsiValue > 70) return 'El RSI está en zona de sobrecompra, indicando una posible corrección a la baja. Considere tomar ganancias.';
    return 'El RSI se encuentra en zona neutral. El activo no muestra condiciones extremas de sobrecompra o sobreventa.';
}

function getMACDInterpretation(macd) {
    if (macd.macd === null) return 'No hay datos suficientes para calcular el MACD.';

    let interpretation = '';
    if (macd.histogram > 0) {
        interpretation = 'El histograma es positivo, indicando momentum alcista. ';
    } else {
        interpretation = 'El histograma es negativo, indicando momentum bajista. ';
    }

    if (macd.trend === 'bullish') {
        interpretation += 'La línea MACD cruzó por encima de la señal, sugiriendo una posible tendencia alcista.';
    } else if (macd.trend === 'bearish') {
        interpretation += 'La línea MACD cruzó por debajo de la señal, sugiriendo una posible tendencia bajista.';
    }

    return interpretation;
}

function getBollingerInterpretation(bb) {
    if (bb.current_price === null) return 'No hay datos suficientes para calcular las Bandas de Bollinger.';

    const price = bb.current_price;
    const upper = bb.upper;
    const lower = bb.lower;
    const middle = bb.middle;

    if (price >= upper) {
        return 'El precio está tocando o superando la banda superior, indicando posible sobrecompra. El precio podría revertir a la baja.';
    } else if (price <= lower) {
        return 'El precio está tocando o por debajo de la banda inferior, indicando posible sobreventa. El precio podría revertir al alza.';
    } else if (price > middle) {
        return 'El precio está por encima de la media móvil pero dentro de las bandas, mostrando fortaleza moderada.';
    } else {
        return 'El precio está por debajo de la media móvil pero dentro de las bandas, mostrando debilidad moderada.';
    }
}

function getBollingerPriceMarker(bb) {
    if (bb.upper === null || bb.lower === null) return '';

    const range = bb.upper - bb.lower;
    const position = ((bb.current_price - bb.lower) / range) * 100;

    return `<div style="position: absolute; top: ${100 - position}%; left: 10px; right: 10px; height: 4px; background: white; box-shadow: 0 0 10px white; border-radius: 2px;"></div>`;
}

function getStochasticInterpretation(stoch) {
    if (stoch.k === null) return 'No hay datos suficientes para calcular el Oscilador Estocástico.';

    let interpretation = '';

    if (stoch.k < 20 && stoch.d < 20) {
        interpretation = 'Ambas líneas están en zona de sobreventa. Posible señal de compra cuando %K cruce por encima de %D.';
    } else if (stoch.k > 80 && stoch.d > 80) {
        interpretation = 'Ambas líneas están en zona de sobrecompra. Posible señal de venta cuando %K cruce por debajo de %D.';
    } else if (stoch.signal === 'bullish_crossover') {
        interpretation = 'Cruce alcista detectado: %K cruzó por encima de %D. Señal de compra.';
    } else if (stoch.signal === 'bearish_crossover') {
        interpretation = 'Cruce bajista detectado: %K cruzó por debajo de %D. Señal de venta.';
    } else {
        interpretation = 'El oscilador está en zona neutral. No hay señales claras de compra o venta en este momento.';
    }

    return interpretation;
}

function translateFactorName(factorName) {
    const translations = {
        'RSI': 'RSI (Índice de Fuerza Relativa)',
        'MACD': 'MACD (Convergencia/Divergencia de Medias Móviles)',
        'News Sentiment': 'Sentimiento de Noticias',
        'Bollinger Bands': 'Bandas de Bollinger',
        'Stochastic': 'Oscilador Estocástico',
        'Volume': 'Volumen',
        'Support Level': 'Nivel de Soporte',
        'Resistance Level': 'Nivel de Resistencia',
        'Moving Average': 'Media Móvil',
        'Price Action': 'Acción del Precio'
    };
    return translations[factorName] || factorName;
}

function translateDescription(description, factorName) {
    // Traducciones de patrones comunes
    const patterns = {
        'at': 'en',
        'indicates neutral conditions': 'indica condiciones neutrales',
        'showing bearish trend': 'muestra tendencia bajista',
        'showing bullish trend': 'muestra tendencia alcista',
        'Based on keyword analysis of': 'Basado en análisis de palabras clave de',
        'articles': 'artículos',
        'RSI at': 'RSI en',
        'MACD showing': 'MACD muestra',
        'bearish': 'bajista',
        'bullish': 'alcista',
        'neutral': 'neutral',
        'oversold': 'sobreventa',
        'overbought': 'sobrecompra'
    };

    let translated = description;
    for (const [eng, esp] of Object.entries(patterns)) {
        translated = translated.replace(new RegExp(eng, 'gi'), esp);
    }

    return translated;
}

function updateSuggestions(predictionData) {
    const container = document.getElementById('suggestions-container');

    if (!predictionData.prediction) {
        container.innerHTML = '<p style="color: #8b949e; text-align: center;">No hay sugerencias disponibles.</p>';
        return;
    }

    const prediction = predictionData.prediction;
    const type = prediction.prediction_type || prediction.signal_type;
    const typeClass = type === 'BUY' ? 'buy' : type === 'SELL' ? 'sell' : 'neutral';
    const typeLabel = type === 'BUY' ? 'COMPRA' : type === 'SELL' ? 'VENTA' : 'MANTENER';
    const confidence = (prediction.confidence_score ? prediction.confidence_score * 100 : prediction.confidence * 100).toFixed(0);

    let html = `
        <div class="suggestion-card ${typeClass}">
            <div class="suggestion-header">
                <span class="suggestion-type ${typeClass}">
                    <i class="fas fa-${type === 'BUY' ? 'arrow-up' : type === 'SELL' ? 'arrow-down' : 'minus'}"></i>
                    ${typeLabel}
                </span>
                <span class="confidence">${confidence}% confianza</span>
            </div>
            <p style="margin-top: 10px; color: #8b949e; font-size: 13px;">
                ${prediction.description || 'Análisis basado en múltiples factores técnicos y fundamentales.'}
            </p>
            <div class="factors">
                <h4 style="font-size: 12px; color: #8b949e; margin-bottom: 10px; text-transform: uppercase;">
                    Factores Clave (XAI):
                </h4>
    `;

    if (prediction.factors && prediction.factors.length > 0) {
        prediction.factors.forEach(factor => {
            // Traducir nombres de factores al español
            const factorNameES = translateFactorName(factor.factor_name);
            const descriptionES = translateDescription(factor.description, factor.factor_name);

            html += `
                <div class="factor-item">
                    <i class="fas fa-check-circle factor-icon"></i>
                    <span><strong>${factorNameES}:</strong> ${descriptionES}</span>
                </div>
            `;
        });
    } else {
        // Generate mock factors based on analysis
        const mockFactors = [
            { name: 'RSI Oversold', desc: 'RSI indica condiciones de sobreventa (< 30)' },
            { name: 'MACD Crossover', desc: 'Cruce alcista en el indicador MACD' },
            { name: 'Volume Spike', desc: 'Incremento significativo en volumen de negociación' },
            { name: 'Support Level', desc: 'Precio cerca de nivel de soporte histórico' }
        ];

        if (type === 'BUY') {
            mockFactors.slice(0, 3).forEach(factor => {
                html += `
                    <div class="factor-item">
                        <i class="fas fa-check-circle factor-icon"></i>
                        <span><strong>${factor.name}:</strong> ${factor.desc}</span>
                    </div>
                `;
            });
        } else if (type === 'SELL') {
            const sellFactors = [
                { name: 'RSI Overbought', desc: 'RSI indica condiciones de sobrecompra (> 70)' },
                { name: 'Bearish Pattern', desc: 'Patrón de velas bajista detectado' },
                { name: 'Resistance Level', desc: 'Precio cerca de nivel de resistencia' }
            ];
            sellFactors.forEach(factor => {
                html += `
                    <div class="factor-item">
                        <i class="fas fa-check-circle factor-icon"></i>
                        <span><strong>${factor.name}:</strong> ${factor.desc}</span>
                    </div>
                `;
            });
        }
    }

    html += `
            </div>
        </div>

        <div style="margin-top: 20px;">
            <h3 style="font-size: 14px; margin-bottom: 15px; color: #58a6ff;">
                <i class="fas fa-chart-line"></i> Patrones Detectados
            </h3>
    `;

    // Mock patterns
    const patterns = [
        { name: 'Double Bottom', confidence: 85, bullish: true },
        { name: 'Higher Lows', confidence: 78, bullish: true }
    ];

    patterns.forEach(pattern => {
        html += `
            <div style="background: #0d1117; padding: 10px; margin-bottom: 8px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 13px;">
                    <i class="fas fa-${pattern.bullish ? 'arrow-trend-up' : 'arrow-trend-down'}"
                       style="color: ${pattern.bullish ? '#3fb950' : '#f85149'}; margin-right: 8px;"></i>
                    ${pattern.name}
                </span>
                <span style="font-size: 12px; color: #8b949e;">${pattern.confidence}%</span>
            </div>
        `;
    });

    html += '</div>';

    container.innerHTML = html;
}

function updatePriceDisplay(data) {
    // Update watchlist prices in real-time
    // This would be connected to actual WebSocket data
}

function updatePortfolioDisplay(data) {
    // Update portfolio summary
    document.getElementById('portfolio-value').textContent = '$' + (data.total_value || 0).toFixed(2);
    document.getElementById('portfolio-change').textContent = (data.change || 0).toFixed(2) + '%';
}

// Tab switching
function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');

    document.getElementById('chart-tab').style.display = tabName === 'chart' ? 'block' : 'none';
    document.getElementById('indicators-tab').style.display = tabName === 'indicators' ? 'block' : 'none';
    document.getElementById('news-tab').style.display = tabName === 'news' ? 'block' : 'none';

    if (tabName === 'news') {
        loadNews();
    }
}

async function loadNews() {
    const container = document.getElementById('news-container');
    container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

    try {
        const response = await fetch('/api/analysis/news/' + currentSymbol);
        const data = await response.json();

        let html = '<h3 style="margin-bottom: 15px;">Análisis de Sentimiento</h3>';

        // Mock news items
        const mockNews = [
            { title: 'Strong Q4 earnings beat expectations', sentiment: 'positive' },
            { title: 'New product launch receives positive reviews', sentiment: 'positive' },
            { title: 'Market concerns about supply chain', sentiment: 'negative' },
            { title: 'Analyst upgrades price target', sentiment: 'positive' }
        ];

        mockNews.forEach(news => {
            html += `
                <div class="news-item ${news.sentiment}">
                    <div class="news-title">${news.title}</div>
                    <div class="news-sentiment">
                        Sentimiento: <strong style="color: ${news.sentiment === 'positive' ? '#3fb950' : '#f85149'}">
                            ${news.sentiment === 'positive' ? 'Positivo' : 'Negativo'}
                        </strong>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<p style="color: #f85149;">Error al cargar noticias</p>';
    }
}

function selectSymbol(symbol) {
    document.getElementById('symbol-search').value = symbol;
    document.querySelectorAll('.watchlist-item').forEach(item => item.classList.remove('active'));
    event.currentTarget.classList.add('active');
    analyzeSymbol();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initWebSocket();
    analyzeSymbol();
});
