# -*- coding: utf-8 -*-
"""
OpenAlgo Technical Indicators - Base Class
"""

import numpy as np
import pandas as pd
from numba import jit
from abc import ABC, abstractmethod
from typing import Union, Tuple, Optional, List

class BaseIndicator(ABC):
    """Base class for all technical indicators"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def calculate(self, *args, **kwargs):
        """Calculate the indicator values"""
        pass
    
    @staticmethod
    def validate_input(data: Union[np.ndarray, pd.Series, list]) -> np.ndarray:
        """
        Validate and convert input data to numpy array
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Input data to validate
            
        Returns:
        --------
        np.ndarray
            Validated numpy array
            
        Raises:
        -------
        TypeError
            If input type is not supported
        ValueError
            If input data is empty
        """
        if isinstance(data, pd.Series):
            return data.values.astype(np.float64)
        elif isinstance(data, list):
            if len(data) == 0:
                raise ValueError("Input data cannot be empty")
            return np.array(data, dtype=np.float64)
        elif isinstance(data, np.ndarray):
            if data.size == 0:
                raise ValueError("Input data cannot be empty")
            return data.astype(np.float64)
        else:
            raise TypeError(f"Invalid input type: {type(data)}. Expected np.ndarray, pd.Series, or list")
    
    @staticmethod
    def validate_period(period: int, data_length: int) -> None:
        """
        Validate period parameter
        
        Parameters:
        -----------
        period : int
            Period value to validate
        data_length : int
            Length of the data array
            
        Raises:
        -------
        ValueError
            If period is invalid
        """
        if not isinstance(period, int):
            raise TypeError(f"Period must be an integer, got {type(period)}")
        if period <= 0:
            raise ValueError(f"Period must be positive, got {period}")
        if period > data_length:
            raise ValueError(f"Period ({period}) cannot be greater than data length ({data_length})")
    
    @staticmethod
    def handle_nan(arr: np.ndarray, fill_value: float = 0.0) -> np.ndarray:
        """
        Handle NaN values in the array
        
        Parameters:
        -----------
        arr : np.ndarray
            Array with potential NaN values
        fill_value : float
            Value to replace NaN with
            
        Returns:
        --------
        np.ndarray
            Array with NaN values handled
        """
        return np.nan_to_num(arr, nan=fill_value)
    
    @staticmethod
    def align_arrays(*arrays: np.ndarray) -> Tuple[np.ndarray, ...]:
        """
        Align multiple arrays to the same length
        
        Parameters:
        -----------
        *arrays : np.ndarray
            Variable number of arrays to align
            
        Returns:
        --------
        Tuple[np.ndarray, ...]
            Tuple of aligned arrays
            
        Raises:
        -------
        ValueError
            If arrays have different lengths
        """
        if not arrays:
            return tuple()
        
        lengths = [len(arr) for arr in arrays]
        if len(set(lengths)) > 1:
            raise ValueError(f"All arrays must have the same length. Got lengths: {lengths}")
        
        return arrays
    
    @staticmethod
    @jit(nopython=True)
    def rolling_window(arr: np.ndarray, window: int) -> np.ndarray:
        """
        Create rolling window view of array (Numba optimized)
        
        Parameters:
        -----------
        arr : np.ndarray
            Input array
        window : int
            Window size
            
        Returns:
        --------
        np.ndarray
            2D array with rolling windows
        """
        shape = arr.shape[:-1] + (arr.shape[-1] - window + 1, window)
        strides = arr.strides + (arr.strides[-1],)
        return np.lib.stride_tricks.as_strided(arr, shape=shape, strides=strides)