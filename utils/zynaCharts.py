import json
import re


async def PieChart(
    chartName,
    title,
    subtitle,
    max_width,
    min_width,
    height,
    background_color,
    borderColor,
    colorByPoint,
    dataLabels_enabled,
    dataLabels_format,
    dataLabels_font_size,
    series_name,
    series_data,
    chart_type="pie",
):
    template = f"""
    <style>
    #{chartName} {{
        min-width: {min_width};
        max-width: {max_width};
        height:{height};

    }}
    </style>

    <div id="{chartName}"></div>
    <script>
        Highcharts.chart('{chartName}', {{
            chart: {{
                type: '{chart_type}',
                backgroundColor: '{background_color}',
                borderColor: '{borderColor}',
                borderWidth: 1,
            }},
            title: {{
            text: '{title}'
            }},
            subtitle: {{
                text: '{subtitle}'
            }},
            tooltip: {{
                valueSuffix: "",
            }},
            credits: {{
            enabled: false
            }},
            legend: {{
                enabled: false
            }},
            plotOptions: {{
                series: {{
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: [
                        {{
                            enabled: {dataLabels_enabled},
                            distance: 20,
                        }},
                        {{
                            enabled: {dataLabels_enabled},
                            distance: -40,
                            format: '{dataLabels_format}',
                            style: {{
                                fontSize: '{dataLabels_font_size}',
                                textOutline: "none",
                                opacity: 0.7,
                            }},
                            filter: {{
                                operator: ">",
                                property: "percentage",
                                value: 1,
                            }},
                        }},
                    ],
                }},
            }},
            series: [
                {{
                    name: '{series_name}',
                    colorByPoint: {colorByPoint},
                    data: {series_data},
                }},
            ],
        }});
    </script>
    """

    template = re.sub(r"\bnan\b", "NaN", template)

    return template


async def LineChart(
    chartName,
    title,
    subtitle,
    max_width,
    min_width,
    height,
    background_color,
    borderColor,
    lineColor,
    xAxisTitle,
    xAxisData,
    yAxisTitle,
    yAxisData,
    dataLabels_enabled,
    dataLabels_format,
    dataLabels_Color,
    gridLineWidth=1,
    chart_type="line",
):
    template = f"""
    <style>
        #{chartName} {{
            min-width: {min_width};
            max-width: {max_width};
            height:{height};

        }}
    </style>

    <div id="{chartName}"></div>

    <script>
        Highcharts.chart('{chartName}', {{
            chart: {{
                backgroundColor: '{background_color}',
                borderColor: '{borderColor}',
                borderWidth: 1,
                type: '{chart_type}',
            }},
            title: {{
                text: '{title}'
            }},
            subtitle: {{
                text: '{subtitle}'
            }},
            xAxis: {{
                title: {{
                    text: '{xAxisTitle}'
                }},
                categories: {xAxisData},
            }},
            yAxis: {{
                gridLineWidth: {gridLineWidth},
                title: {{
                    text: '{yAxisTitle}'
                }}
            }},
            credits: {{
                enabled: false
            }},
            legend: {{
                enabled: false
            }},
            plotOptions: {{
                line: {{
                    allowPointSelect: true,
                    enableMouseTracking: true,
                }}
            }},
            series: [{{
                name: '',
                data: {yAxisData},
                color: '{lineColor}',
                dataLabels: {{
                    enabled: {dataLabels_enabled},
                    color: '{dataLabels_Color}',
                    format: '{dataLabels_format}',

                }},
            }}]
        }});
    </script>
    """

    template = re.sub(r"\bnan\b", "NaN", template)

    return template


async def SplineChart(
    chartName,
    title,
    subtitle,
    max_width,
    min_width,
    height,
    background_color,
    borderColor,
    lineColor,
    xAxisTitle,
    xAxisData,
    yAxisTitle,
    yAxisData,
    dataLabels_enabled,
    dataLabels_format,
    dataLabels_Color,
    gridLineWidth=0,
    chart_type="spline",
):
    template = f"""
    <style>
        #{chartName} {{
            min-width: {min_width};
            max-width: {max_width};
            height:{height};

        }}
    </style>

    <div id="{chartName}"></div>

    <script>
        Highcharts.chart('{chartName}', {{
            chart: {{
                backgroundColor: '{background_color}',
                borderColor: '{borderColor}',
                borderWidth: 1,
                type: '{chart_type}',
            }},
            title: {{
                text: '{title}'
            }},
            subtitle: {{
                text: '{subtitle}'
            }},
            xAxis: {{
                title: {{
                    text: '{xAxisTitle}'
                }},
                categories: {xAxisData},
            }},
            yAxis: {{
                gridLineWidth: {gridLineWidth},
                title: {{
                    text: '{yAxisTitle}'
                }}
            }},
            credits: {{
                enabled: false
            }},
            legend: {{
                enabled: false
            }},
            plotOptions: {{
                line: {{
                    smooth: true,
                    enableMouseTracking: true,
                }}
            }},
            series: [{{
                name: '',
                data: {yAxisData},
                color: '{lineColor}',
                dataLabels: {{
                    enabled: {dataLabels_enabled},
                    color: '{dataLabels_Color}',
                    format: '{dataLabels_format}',

                }},
            }}]
        }});
    </script>
    """

    template = re.sub(r"\bnan\b", "NaN", template)

    return template


async def MultiLineChart(
    chartName,
    title,
    subtitle,
    max_width,
    min_width,
    height,
    background_color,
    borderColor,
    xAxisTitle,
    xAxisData,
    yAxisTitle,
    yAxisName1,
    yAxisData1,
    lineColor1,
    yAxisName2,
    yAxisData2,
    lineColor2,
    dataLabels_enabled,
    dataLabels_format,
    dataLabels_Color,
    gridLineWidth=1,
    chart_type="line",
):
    template = f"""
    <style>
        #{chartName} {{
            min-width: {min_width};
            max-width: {max_width};
            height:{height};

        }}
    </style>

    <div id="{chartName}"></div>

    <script>
        Highcharts.chart('{chartName}', {{
            chart: {{
                backgroundColor: '{background_color}',
                borderColor: '{borderColor}',
                borderWidth: 1,
                type: '{chart_type}',
            }},
            title: {{
                text: '{title}'
            }},
            subtitle: {{
                text: '{subtitle}'
            }},
            xAxis: {{
                title: {{
                    text: '{xAxisTitle}'
                }},
                categories: {xAxisData},
            }},
            yAxis: {{
                gridLineWidth: {gridLineWidth},
                title: {{
                    text: '{yAxisTitle}'
                }}
            }},
            credits: {{
                enabled: false
            }},
            legend: {{
                enabled: true
            }},
            plotOptions: {{
                line: {{
                    smooth: true,
                    enableMouseTracking: true,
                }}
            }},
            series: [{{
                name: '{yAxisName1}',
                data: {yAxisData1},
                color: '{lineColor1}',
                dataLabels: {{
                    enabled: {dataLabels_enabled},
                    color: '{dataLabels_Color}',
                    format: '{dataLabels_format}',

                }},
            }},
            {{
                name: '{yAxisName2}',
                data: {yAxisData2},
                color: '{lineColor2}',
                dataLabels: {{
                    enabled: {dataLabels_enabled},
                    color: '{dataLabels_Color}',
                    format: '{dataLabels_format}',

                }},
            }}]
        }});
    </script>
    """

    template = re.sub(r"\bnan\b", "NaN", template)

    return template


async def MultiSplineChart(
    chartName,
    title,
    subtitle,
    max_width,
    min_width,
    height,
    background_color,
    borderColor,
    xAxisTitle,
    xAxisData,
    yAxisTitle,
    yAxisName1,
    yAxisData1,
    lineColor1,
    yAxisName2,
    yAxisData2,
    lineColor2,
    dataLabels_enabled,
    dataLabels_format,
    dataLabels_Color,
    gridLineWidth=0,
    chart_type="spline",
):
    template = f"""
    <style>
        #{chartName} {{
            min-width: {min_width};
            max-width: {max_width};
            height:{height};

        }}
    </style>

    <div id="{chartName}"></div>

    <script>
        Highcharts.chart('{chartName}', {{
            chart: {{
                backgroundColor: '{background_color}',
                borderColor: '{borderColor}',
                borderWidth: 1,
                type: '{chart_type}',
            }},
            title: {{
                text: '{title}'
            }},
            subtitle: {{
                text: '{subtitle}'
            }},
            xAxis: {{
                title: {{
                    text: '{xAxisTitle}'
                }},
                categories: {xAxisData},
            }},
            yAxis: {{
                gridLineWidth: {gridLineWidth},
                title: {{
                    text: '{yAxisTitle}'
                }}
            }},
            credits: {{
                enabled: false
            }},
            legend: {{
                enabled: false
            }},
            plotOptions: {{
                line: {{
                    smooth: true,
                    enableMouseTracking: true,
                }}
            }},
            series: [{{
                name: '{yAxisName1}',
                data: {yAxisData1},
                color: '{lineColor1}',
                dataLabels: {{
                    enabled: {dataLabels_enabled},
                    color: '{dataLabels_Color}',
                    format: '{dataLabels_format}',

                }},

            }},
            {{
                name: '{yAxisName2}',
                data: {yAxisData2},
                color: '{lineColor2}',
                dataLabels: {{
                    enabled: {dataLabels_enabled},
                    color: '{dataLabels_Color}',
                    format: '{dataLabels_format}',

                }},

            }}]
        }});
    </script>
    """

    template = re.sub(r"\bnan\b", "NaN", template)

    return template


async def BarChart(
    chartName,
    title,
    subtitle,
    max_width,
    min_width,
    height,
    background_color,
    borderColor,
    lineColor,
    colorByPoint,
    xAxisTitle,
    xAxisData,
    yAxisTitle,
    yAxisData,
    dataLabels_enabled,
    dataLabels_format,
    dataLabels_Color,
    dataLabels_font_size,
    gridLineWidth=1,
    chart_type="bar",
):
    template = f"""
    <style>
        #{chartName} {{
            min-width: {min_width};
            max-width: {max_width};
            height:{height};

        }}
    </style>

    <div id="{chartName}"></div>

    <script>
        Highcharts.chart('{chartName}', {{
            chart: {{
                backgroundColor: '{background_color}',
                borderColor: '{borderColor}',
                borderWidth: 1,
                type: '{chart_type}',
            }},
            title: {{
                text: '{title}'
            }},
            subtitle: {{
                text: '{subtitle}'
            }},
            xAxis: {{
                title: {{
                    text: '{xAxisTitle}'
                }},
                categories: {xAxisData},
            }},
            yAxis: {{
                gridLineWidth: {gridLineWidth},
                title: {{
                    text: '{yAxisTitle}'
                }}
            }},
            credits: {{
                enabled: false
            }},
            legend: {{
                enabled: false
            }},
            plotOptions: {{
                line: {{
                    enableMouseTracking: true
                }}
            }},
            series: [{{
                name: '',
                data: {yAxisData},
                color: '{lineColor}',
                colorByPoint: {colorByPoint},
                dataLabels: {{
                    enabled: {dataLabels_enabled},
                    format: '{dataLabels_format}',
                    style: {{
                            color: '{dataLabels_Color}',
                            fontSize: '{dataLabels_font_size}',
                    }}
                }},
            }}]
        }});
    </script>
    """

    template = re.sub(r"\bnan\b", "NaN", template)

    return template


async def ColumnChart(
    chartName,
    title,
    subtitle,
    max_width,
    min_width,
    height,
    background_color,
    borderColor,
    lineColor,
    colorByPoint,
    xAxisTitle,
    xAxisData,
    yAxisTitle,
    yAxisData,
    dataLabels_enabled,
    dataLabels_format,
    dataLabels_Color,
    dataLabels_font_size,
    dataLabels_rotation,
    dataLabels_align,
    dataLabels_padding,
    gridLineWidth=1,
    chart_type="column",
):
    template = f"""
    <style>
        #{chartName} {{
            min-width: {min_width};
            max-width: {max_width};
            height:{height};
        }}
    </style>

    <div id="{chartName}"></div>

    <script>
        Highcharts.chart('{chartName}', {{
            chart: {{
                backgroundColor: '{background_color}',
                borderColor: '{borderColor}',
                borderWidth: 1,
                type: '{chart_type}',
            }},
            title: {{
                text: '{title}'
            }},
            subtitle: {{
                text: '{subtitle}'
            }},
            xAxis: {{
                title: {{
                    text: '{xAxisTitle}'
                }},
                categories: {xAxisData},
            }},
            yAxis: {{
                gridLineWidth: {gridLineWidth},
                title: {{
                    text: '{yAxisTitle}'
                }}
            }},
            credits: {{
                enabled: false
            }},
            legend: {{
                enabled: false
            }},
            plotOptions: {{
                line: {{
                    enableMouseTracking: true
                }}
            }},
            series: [{{
                name: '',
                data: {yAxisData},
                color: '{lineColor}',
                colorByPoint: {colorByPoint},
                dataLabels: {{
                    enabled: {dataLabels_enabled},
                    rotation: {dataLabels_rotation},
                    align: '{dataLabels_align}',
                    y: {dataLabels_padding},
                    format: '{dataLabels_format}',
                    style: {{
                            color: '{dataLabels_Color}',
                            fontSize: '{dataLabels_font_size}',
                    }}
                }},
            }}]
        }});
    </script>
    """

    template = re.sub(r"\bnan\b", "NaN", template)

    return template


async def MultiColumnChart(
    chartName,
    title,
    subtitle,
    max_width,
    min_width,
    height,
    background_color,
    borderColor,
    lineColor1,
    lineColor2,
    colorByPoint,
    xAxisTitle,
    xAxisData,
    yAxisTitle,
    yAxisData1,
    yAxisData2,
    dataLabels_enabled,
    dataLabels_format,
    dataLabels_Color1,
    dataLabels_Color2,
    dataLabels_font_size,
    dataLabels_rotation,
    dataLabels_align,
    dataLabels_padding,
    gridLineWidth=1,
    chart_type="column",
):
    template = f"""
    <style>
        #{chartName} {{
            min-width: {min_width};
            max-width: {max_width};
            height:{height};
        }}
    </style>

    <div id="{chartName}"></div>

    <script>
        Highcharts.chart('{chartName}', {{
            chart: {{
                backgroundColor: '{background_color}',
                borderColor: '{borderColor}',
                borderWidth: 1,
                type: '{chart_type}',
            }},
            title: {{
                text: '{title}'
            }},
            subtitle: {{
                text: '{subtitle}'
            }},
            xAxis: {{
                title: {{
                    text: '{xAxisTitle}'
                }},
                categories: {xAxisData},
            }},
            yAxis: {{
                gridLineWidth: {gridLineWidth},
                title: {{
                    text: '{yAxisTitle}'
                }}
            }},
            credits: {{
                enabled: false
            }},
            legend: {{
                enabled: false
            }},
            plotOptions: {{
                line: {{
                    enableMouseTracking: true
                }}
            }},
            series: [{{
                name: '',
                data: {yAxisData1},
                color: '{lineColor1}',
                colorByPoint: {colorByPoint},
                dataLabels: {{
                    enabled: {dataLabels_enabled},
                    rotation: {dataLabels_rotation},
                    align: '{dataLabels_align}',
                    y: {dataLabels_padding},
                    format: '{dataLabels_format}',
                    style: {{
                            color: '{dataLabels_Color1}',
                            fontSize: '{dataLabels_font_size}',
                    }}
                }},

            }},
            {{
                name: '',
                data: {yAxisData2},
                color: '{lineColor2}',
                colorByPoint: {colorByPoint},
                dataLabels: {{
                    enabled: {dataLabels_enabled},
                    rotation: {dataLabels_rotation},
                    align: '{dataLabels_align}',
                    y: {dataLabels_padding},
                    format: '{dataLabels_format}',
                    style: {{
                            color: '{dataLabels_Color2}',
                            fontSize: '{dataLabels_font_size}',
                    }}
                }},

            }}]
        }});
    </script>
    """

    template = re.sub(r"\bnan\b", "NaN", template)

    return template
