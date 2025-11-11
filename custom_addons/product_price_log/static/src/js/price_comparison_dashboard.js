/** @odoo-module **/

import { Component, onWillStart, onMounted, useRef, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { loadJS, loadCSS } from "@web/core/assets";

class PriceComparisonDashboard extends Component {
    static props = {
        action: { type: Object, optional: true },
        actionId: { type: Number, optional: true },
        className: { type: String, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.chartCanvas = useRef("chartCanvas");
        this.productSelect = useRef("productSelect");
        this.competitorSelect = useRef("competitorSelect");
        this.startDate = useRef("startDate");
        this.endDate = useRef("endDate");

        this.state = useState({
            chartDataRaw: [],
            chartData: {},
            allProducts: [],
            allCompetitors: [],
            viewMode: "trend", // "trend" or "comparison"
            chartType: "line", // default chart type
            loading: true,
        });

        this.chart = null;

        // Bind methods
        this.applyFilter = this.applyFilter.bind(this);
        this.switchView = this.switchView.bind(this);
        this.switchChart = this.switchChart.bind(this);

        onWillStart(async () => {
            await Promise.all([
                loadJS("/product_price_log/static/lib/chartjs/Chart.js"),
                loadJS("/product_price_log/static/src/js/select2.min.js"),
                loadCSS("/product_price_log/static/src/css/select2.min.css"),
            ]);
        });

        onMounted(async () => {
            await this.populateSelects();
            this.initializeSelect2();
            await this.applyFilter();
        });
    }

    async populateSelects() {
        try {
            const result = await this.orm.call(
                "price.comparison.report",
                "get_price_comparison_data",
                []
            );

            this.state.allProducts = result.products || [];
            this.state.allCompetitors = result.competitors || [];

            const productSelect = this.productSelect.el;
            const competitorSelect = this.competitorSelect.el;

            if (productSelect) {
                productSelect.innerHTML = "";
                this.state.allProducts.forEach((p) => {
                    const opt = document.createElement("option");
                    opt.value = p.id;
                    opt.textContent = p.name;
                    productSelect.appendChild(opt);
                });
            }

            if (competitorSelect) {
                competitorSelect.innerHTML = "";
                this.state.allCompetitors.forEach((c) => {
                    const opt = document.createElement("option");
                    opt.value = c.id;
                    opt.textContent = c.name;
                    competitorSelect.appendChild(opt);
                });
            }
        } catch (err) {
            console.error("Error populating selects:", err);
        }
    }

    initializeSelect2() {
        if (this.productSelect.el && this.competitorSelect.el) {
            $(this.productSelect.el).select2({
                placeholder: "Select Products",
                allowClear: true,
                width: "100%",
            }).on("change", () => this.applyFilter());

            $(this.competitorSelect.el).select2({
                placeholder: "Select Competitors",
                allowClear: true,
                width: "100%",
            }).on("change", () => this.applyFilter());
        }
    }

    switchView(mode) {
        this.state.viewMode = mode;

        // Set default chart type for view if user hasn't selected manually
        if (mode === "trend" && !['bar','line','pie'].includes(this.state.chartType)) {
            this.state.chartType = 'line';
        }
        if (mode === "comparison" && !['bar','line','pie'].includes(this.state.chartType)) {
            this.state.chartType = 'bar';
        }

        this.applyFilter();
    }

    switchChart(type) {
        this.state.chartType = type.toLowerCase();
        this.renderChart();
    }

    async applyFilter() {
        this.state.loading = true;
        if (this.chart) this.chart.destroy();

        try {
            const productIds = Array.from(this.productSelect.el.selectedOptions).map(opt => parseInt(opt.value));
            const competitorIds = Array.from(this.competitorSelect.el.selectedOptions).map(opt => parseInt(opt.value));
            const startDateValue = this.startDate.el.value;
            const endDateValue = this.endDate.el.value;

            const data = await this.orm.call(
                "price.comparison.report",
                "get_price_comparison_data",
                [[], productIds, competitorIds, startDateValue, endDateValue]
            );

            this.state.chartDataRaw = data.price_data || [];

            if (this.state.viewMode === "comparison") {
                this.state.chartData = this.processDataForGroupedChart(this.state.chartDataRaw);
            } else {
                this.state.chartData = this.processDataForTrendChart(this.state.chartDataRaw);
            }

            this.renderChart();
        } catch (err) {
            console.error("Error applying filter:", err);
        } finally {
            this.state.loading = false;
        }
    }

    processDataForTrendChart(priceData) {
        if (!priceData || priceData.length === 0) return { labels: [], datasets: [] };

        // Group data by competitor (AMG / Competitor) over time
        const dateSet = [...new Set(priceData.map(p => p.date))].sort(); // X-axis = dates
        const companies = [...new Set(priceData.map(p => p.source === 'your' ? 'AMG' : (p.competitor_id ? p.competitor_id[1] : 'Unknown')))];

        const datasets = companies.map((company, index) => {
            const data = dateSet.map(date => {
                // Average price of all products for that company on this date
                const items = priceData.filter(p => {
                    const comp = p.source === 'your' ? 'AMG' : (p.competitor_id ? p.competitor_id[1] : 'Unknown');
                    return p.date === date && comp === company;
                });
                if (!items.length) return null;
                return items.reduce((sum, i) => sum + i.price, 0) / items.length;
            });

            const hue = (company === 'AMG' ? 0 : (index * 137.5) % 360);
            const color = `hsl(${hue},70%,50%)`;

            return {
                label: company,
                data,
                borderColor: color,
                backgroundColor: color + '33',
                borderWidth: 2,
                tension: 0.2,
                fill: false,
            };
        });

        return { labels: dateSet, datasets };
    }



    processDataForGroupedChart(priceData) {
        if (!priceData || priceData.length === 0) return { labels: [], datasets: [] };

        const latestDate = [...new Set(priceData.map(p => p.date))].sort().pop();
        const filtered = priceData.filter(p => p.date === latestDate);

        const products = [...new Set(filtered.map(p => p.product_id ? p.product_id[1] : 'Unknown'))];
        const competitors = [...new Set(filtered.map(p =>
            p.source === 'your' ? 'AMG' : (p.competitor_id ? p.competitor_id[1] : 'Unknown')
        ))];

        const datasets = competitors.map((comp, i) => {
            const data = products.map(prod => {
                const match = filtered.find(p =>
                    (p.product_id ? p.product_id[1] : '') === prod &&
                    (p.source === 'your' ? 'AMG' : (p.competitor_id ? p.competitor_id[1] : 'Unknown')) === comp
                );
                return match ? match.price : 0;
            });
            const hue = (comp === 'AMG' ? 0 : (i * 137.5) % 360);
            const color = `hsl(${hue},70%,50%)`;
            return { label: comp, data, backgroundColor: color };
        });

        return { labels: products, datasets };
    }

    renderChart() {
        if (this.chart) this.chart.destroy();
        if (!this.chartCanvas.el) return;

        try {
            const ctx = this.chartCanvas.el.getContext("2d");
            this.chart = new Chart(ctx, {
                type: this.state.chartType || (this.state.viewMode === 'comparison' ? 'bar' : 'line'),
                data: this.state.chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top' },
                        title: {
                            display: true,
                            text: this.state.viewMode === 'comparison'
                                ? "Product vs Competitor Price Comparison"
                                : "Price Trend Over Time",
                        },
                        tooltip: {
                            callbacks: {
                                label: (context) => {
                                    const datasetLabel = context.dataset.label || "";
                                    const value = context.parsed?.y ?? context.parsed;

                                    // Access the original data item
                                    const dataIndex = context.dataIndex;
                                    const item = this.state.chartDataRaw[dataIndex]; // priceData from the state
                                    const productName = item?.product_id ? item.product_id[1] : "Unknown";
                                    const companyName = item?.source === "your" ? "AMG" : (item?.competitor_id ? item.competitor_id[1] : "Unknown");

                                    return `${companyName} - ${productName}: ${value?.toLocaleString()}`;
                                },
                            },
                        },

                    },
                    scales: {
                        x: { title: { display: true, text: this.state.viewMode === 'comparison' ? 'Products' : 'Date' } },
                        y: { title: { display: true, text: 'Price' }, beginAtZero: false },
                    }
                }
            });
        } catch (err) {
            console.error("Chart render error:", err);
        } finally {
            this.state.loading = false;
        }
    }
}

PriceComparisonDashboard.template = "product_price_log.Dashboard";
registry.category("actions").add("price_comparison_dashboard_action", PriceComparisonDashboard);
