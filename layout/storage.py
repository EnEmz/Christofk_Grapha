# storage.py

from dash import dcc


def get_storage(id, storage_type='memory', initial_data=None):
    return dcc.Store(id = id, storage_type = storage_type, data=initial_data)
    
# Define all of your storage components here
def build_storage_components():
    storage_components = []
    
    # For data storage
    storage_components.append(get_storage('store-data-pool', 'local'))
    storage_components.append(get_storage('store-data-iso', 'local'))
    storage_components.append(get_storage('store-data-lingress', 'local'))
    
    # For user selection
    storage_components.append(get_storage('store-metabolite-ratios'))
    storage_components.append(get_storage('store-data-order'))
    storage_components.append(get_storage('store-met-classes'))
    storage_components.append(get_storage('store-data-normalization'))
    storage_components.append(get_storage('store-met-groups'))
    
    # For settings
    storage_components.append(get_storage('store-bulk-heatmap-settings'))
    storage_components.append(get_storage('store-bulk-isotopologue-heatmap-settings'))
    storage_components.append(get_storage('store-custom-heatmap-settings'))
    storage_components.append(get_storage('store-settings-metabolomics'))
    storage_components.append(get_storage('store-settings-isotopologue-distribution'))
    storage_components.append(get_storage('store-volcano-settings'))
    storage_components.append(get_storage('store-settings-lingress'))
    
    # For plots
    storage_components.append(get_storage('store-bulk-heatmap-plot'))
    storage_components.append(get_storage('store-bulk-isotopologue-heatmap-plot'))
    storage_components.append(get_storage('store-custom-heatmap-plot'))
    storage_components.append(get_storage('store-volcano-plot'))
    
    # For statistics
    storage_components.append(get_storage('store-p-value-metabolomics'))
    storage_components.append(get_storage('store-p-value-isotopologue-distribution'))
    
    # For plot manipulation
    storage_components.append(get_storage('store-volcano-clicked-datapoints'))
    storage_components.append(get_storage('store-isotopologue-distribution-selection'))
    
    # For user actions
    storage_components.append(get_storage('store-download-data-selection'))
    storage_components.append(get_storage('store-download-config'))
    storage_components.append(get_storage('store-user-metabolite-ratio-cleared', 'memory', {'cleared': False}))
    
    return storage_components
    
    
    
    
    
    
    
    
    
