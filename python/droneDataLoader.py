import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

from scipy import signal

class DroneDataLoader:
    def __init__(self, data_path='..'):
        self.data_path = data_path
        self.index_path = os.path.join(data_path, 'data/dataset_index.csv')
        if not os.path.exists(self.index_path):
            print(f"Index file not found at {self.index_path}")
            return
        
        self.df = pd.read_csv(self.index_path)
        print(f"Registry successfully loaded. Available records: {len(self.df)}")

    def get_samples(self, category=None, freq=None):
        filtered = self.df
        if category:
            filtered = filtered[filtered['category'] == category]
        if freq:
            filtered = filtered[filtered['freq_ghz'] == freq]
        return filtered
    
    def load_data_pair(self, row):
        vtx_path = os.path.join(self.data_path, row['csv_vtx_path'].lstrip('./')) if pd.notna(row['csv_vtx_path']) else None
        vrx_path = os.path.join(self.data_path, row['csv_vrx_path'].lstrip('./'))
        
        vtx = pd.read_csv(vtx_path, skiprows=1) if vtx_path else None
        vrx = pd.read_csv(vrx_path, skiprows=1)
        
        return vtx, vrx
    
    def plot_comparative_analysis(self, row, start_time_s = 0, end_time_s=0.2):
        vtx, vrx = self.load_data_pair(row)
        vtx = self.normalize_signal(vtx)
        vrx = self.normalize_signal(vrx, window_size=7_000)
        
        mask_time = (vrx['Second'] >= start_time_s) & (vrx['Second'] <= end_time_s)
        
        fig = plt.figure(figsize=(18, 6))
        gs = fig.add_gridspec(1, 2, width_ratios=[3, 2])
        
        ax1 = fig.add_subplot(gs[0, 0])
        
        ax1.plot(vrx[mask_time]['Second'] * 10e3, vrx[mask_time]['Value'], 
                 label='VRX (Received)', color='tab:blue', alpha=0.4, lw=1)
        
        if vtx is not None:
            ax1.plot(vtx[mask_time]['Second'] * 10e3, vtx[mask_time]['Value'], 
                     label='VTX (Original)', color='tab:green', alpha=0.4, lw=1)
        
        ax1.set_title(f"Signal Comparison: Sample {row['idx']} ({row['freq_ghz']} GHz)")
        ax1.set_xlabel("Time (ms)")
        ax1.set_ylabel("Normalized Amplitude")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        ax2 = fig.add_subplot(gs[0, 1])
        img_path = os.path.join(self.data_path, row['img_path'].lstrip('./'))
        if os.path.exists(img_path):
            img = mpimg.imread(img_path)
            ax2.imshow(img)
            ax2.set_title("Visual Confirmation")
            ax2.axis('off')
        else:
            ax2.text(0.5, 0.5, "Image not found", ha='center', va='center')
            
        plt.tight_layout()
        plt.show()

    @staticmethod
    def normalize_signal(df, window_size=1_000_000):
        if df is None: return None
        data = df['Value'].values
        normalized = np.zeros_like(data)
    
        for i in range(0, len(data), window_size):
            end = min(i + window_size, len(data))
            window = data[i:end]

            normalized[i:end] = (window - np.min(window)) / (np.max(window) - np.min(window))

        new_df = df.copy()
        new_df['Value'] = normalized
        return new_df

    @staticmethod
    def calculate_snr(vtx_df, vrx_df):
        if vtx_df is None or vrx_df is None:
            return None

        s_ideal = vtx_df['Value'].values
        s_noisy = vrx_df['Value'].values

        noise = s_noisy - s_ideal
        
        p_signal = np.var(s_ideal)
        p_noise = np.var(noise)

        if p_noise == 0:
            return float('inf')

        snr_db = 10 * np.log10(p_signal / p_noise)
        return snr_db

