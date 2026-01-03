#!/usr/bin/env python3

import numpy as np
import os

def test_numpy():
    print("🧪 Testing numpy functionality...")
    
    # Test basic numpy operations
    try:
        arr = np.array([1, 2, 3, 4, 5])
        print(f"✅ Basic numpy array: {arr}")
        
        # Test saving and loading
        test_file = "test_numpy.npy"
        np.save(test_file, arr)
        loaded_arr = np.load(test_file)
        print(f"✅ Save/load test: {loaded_arr}")
        
        # Clean up
        os.remove(test_file)
        print("✅ Numpy is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Numpy error: {e}")
        return False

def test_feature_loading():
    print("\n🧪 Testing feature loading...")
    
    try:
        # Try to load the features
        features_data = np.load("part_image_embeddings.npy", allow_pickle=True)
        print(f"✅ Features loaded successfully: {len(features_data)} feature sets")
        
        # Try to access the first feature
        first_feature = features_data[0]
        print(f"✅ First feature keys: {list(first_feature.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Feature loading error: {e}")
        return False

if __name__ == "__main__":
    test_numpy()
    test_feature_loading() 