import re


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
    dataLabels_Color,
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
    dataLabels_Color,
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
    dataLabels_Color,
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

                }},
            }},
            {{
                name: '{yAxisName2}',
                data: {yAxisData2},
                color: '{lineColor2}',
                dataLabels: {{
                    enabled: {dataLabels_enabled},
                    color: '{dataLabels_Color}',

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
    dataLabels_Color,
    dataLabels_font_size,
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
                    animation: {{defer: 6000}},
                    format: '{{point.y:.1f}}',
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
    dataLabels_Color,
    dataLabels_font_size,
    dataLabels_rotation,
    dataLabels_align,
    dataLabels_padding,
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
                    format: '{{point.y:.1f}}',
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
    dataLabels_Color1,
    dataLabels_Color2,
    dataLabels_font_size,
    dataLabels_rotation,
    dataLabels_align,
    dataLabels_padding,
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
                    format: '{{point.y:.1f}}',
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
                    format: '{{point.y:.1f}}',
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
