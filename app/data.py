from typing import List
import pandas as pd
import matplotlib.pyplot as plt



class frameViewDataAnalyser:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def getCols(self) -> List[str]:
        # Returns a list of columns in the dataframe
        return list(self.df.columns)

    def getAvgLatency(self) -> float:
        # Returns the average latency from the dataframe
        return self.df['MsRenderPresentLatency'].mean() if 'MsRenderPresentLatency' in self.df else None

    def getAvgFPS(self) -> float:
        # Returns the average FPS from the dataframe
        return self.df['FPS'].mean() if 'FPS' in self.df else None

    def getAvgFrametime(self) -> float:
        # Returns the average frametime from the dataframe
        return self.df['Frametime'].mean() if 'Frametime' in self.df else None

    def getLineGraph(self, y_plots: List[str], x_plot: str) -> plt:
        plt.figure(figsize=(10, 6))
        for y_plot in y_plots:
            plt.plot(self.df[x_plot], self.df[y_plot], label=y_plot)
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        return plt
