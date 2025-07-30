import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from ipywidgets import HBox, VBox, IntSlider, Dropdown
from IPython.display import display, clear_output


class MiningVisualizer:
    def __init__(self, df, continuous_columns, discrete_columns,
                 width=1000, height=600, subset=['X', 'Y', 'Z'], marker_size=6,
                 η=0.15, colab=False, eyex=1.5, eyey=-1.2, eyez=1.8):
        
        self.df = df
        self.continuous_columns = continuous_columns
        self.discrete_columns = discrete_columns
        self.x, self.y, self.z = subset
        self.marker_size = marker_size
        self.η = η
        self.colab = colab
        self.eyex = eyex
        self.eyey = eyey
        self.eyez = eyez

        x_range = df[self.x].max() - df[self.x].min()
        y_range = df[self.y].max() - df[self.y].min()
        z_range = df[self.z].max() - df[self.z].min()

        self.xlim = (df[self.x].min() - η * x_range, df[self.x].max() + η * x_range)
        self.ylim = (df[self.y].min() - η * y_range, df[self.y].max() + η * y_range)
        self.zlim = (df[self.z].min() - η * z_range, df[self.z].max() + η * z_range)

        self.fig = go.FigureWidget(make_subplots(specs=[[{'is_3d': True}]]))
        self.fig.layout.width = width
        self.fig.layout.height = height
        self.fig.update_layout(scene=dict(
            xaxis=dict(range=self.xlim),
            yaxis=dict(range=self.ylim),
            zaxis=dict(range=self.zlim),
            camera=dict(eye=dict(x=eyex, y=eyey, z=eyez))
        ))

        self.filter_type_dropdown = Dropdown(options=['None', 'Continuous', 'Discrete'], value='None', description='Filter Type:')
        self.variable_dropdown = Dropdown(options=[], description='Variable:', visible=False)
        self.marker_size_slider = IntSlider(value=marker_size, min=1, max=20, step=1, description='Marker Size:')

        self.filter_type_dropdown.observe(self.update_ui, names='value')
        self.variable_dropdown.observe(self.update_plot, names='value')
        self.marker_size_slider.observe(self.update_marker_size, names='value')

    def update_ui(self, change):
        ftype = self.filter_type_dropdown.value
        if ftype == 'Continuous':
            self.variable_dropdown.options = self.continuous_columns
        elif ftype == 'Discrete':
            self.variable_dropdown.options = self.discrete_columns
        else:
            self.variable_dropdown.options = []
        self.update_plot(None)

    def update_marker_size(self, change):
        self.marker_size = self.marker_size_slider.value
        self.update_plot(None)

    def update_plot(self, change):
        self.fig.data = []
        ftype = self.filter_type_dropdown.value
        var = self.variable_dropdown.value
        subset = [self.x, self.y, self.z] + ([var] if var else [])
        df = self.df.dropna(subset=subset)

        trace = dict(x=df[self.x], y=df[self.y], z=df[self.z],
                     mode='markers', marker=dict(size=self.marker_size))

        if ftype == 'Discrete' and var:
            for category in sorted(df[var].unique()):
                d = df[df[var] == category]
                trace['x'], trace['y'], trace['z'] = d[self.x], d[self.y], d[self.z]
                trace['name'] = f'{var}: {category}'
                self.fig.add_trace(go.Scatter3d(**trace))
        elif ftype == 'Continuous' and var:
            trace['marker']['color'] = df[var]
            trace['marker']['colorscale'] = 'Turbo'
            trace['marker']['colorbar'] = dict(title=var)
            trace['hovertemplate'] = (
                f"<b>{self.x}:</b> %{{x}}<br>"
                f"<b>{self.y}:</b> %{{y}}<br>"
                f"<b>{self.z}:</b> %{{z}}<br>"
                f"<b>{var}:</b> %{{marker.color}}<extra></extra>")
            self.fig.add_trace(go.Scatter3d(**trace))
        else:
            self.fig.add_trace(go.Scatter3d(**trace))

    def show(self):
        self.ui = VBox([HBox([self.filter_type_dropdown, self.variable_dropdown]), self.marker_size_slider])
        if self.colab:
            from google.colab import output
            output.enable_custom_widget_manager()
            display(self.ui)
        else:
            display(self.ui, self.fig)
        self.update_plot(None)

    def save(self, file_name="visualization.html"):
        self.fig.write_html(file_name)
        print(f"Visualization saved to {file_name}")


def plot_drillholes_3d(drillhole_df):
    fig = go.Figure()
    for bhid, group in drillhole_df.groupby('BHID'):
        fig.add_trace(go.Scatter3d(
            x=group['X'], y=group['Y'], z=group['Z'],
            mode='lines', line=dict(width=8),
            name=bhid, text=bhid, hoverinfo='text'
        ))

    fig.update_layout(scene=dict(
        xaxis_title='X', yaxis_title='Y', zaxis_title='Z'
    ), title='3D Drillhole Plot')
    return fig
