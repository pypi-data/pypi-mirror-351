"""
save_results.py – centralised persistence + reporting utilities

This module is the **single exit point** for anything that needs to hit disk after an optimisation
run.  It intentionally concentrates all I/O – spreadsheets, JSON dumps, plots – so that the rest of
the codebase can remain side-effect free and therefore easier to test.

Key responsibilities
• Convert rich in-memory Python/Pandas objects into human-readable artefacts (Excel/JSON).
• Produce quick-look diagnostics such as demand/load histograms and interactive Folium maps.
• Guarantee the results directory structure exists and file names are timestamp-safe.

By funnelling output through one module we avoid scattered `to_excel` / `to_json` calls and keep the
pipeline composable – exactly the kind of "one obvious place" Jeff Dean and John Ousterhout
advocate for.
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
from fleetmix.config.parameters import Parameters
import json
import numpy as np
import seaborn as sns
import ast
import folium
from typing import Dict
from fleetmix.core_types import BenchmarkType, VRPSolution
from fleetmix.utils.logging import FleetmixLogger

logger = FleetmixLogger.get_logger(__name__)

def save_optimization_results(
    execution_time: float,
    solver_name: str,
    solver_status: str,
    configurations_df: pd.DataFrame,
    selected_clusters: pd.DataFrame,
    total_fixed_cost: float,
    total_variable_cost: float,
    total_light_load_penalties: float,
    total_compartment_penalties: float,
    total_penalties: float,
    vehicles_used: pd.Series,
    missing_customers: set,
    parameters: Parameters,
    filename: str = None,
    format: str = 'excel',
    is_benchmark: bool = False,
    expected_vehicles: int | None = None,
    solver_runtime_sec: float = None,
    post_optimization_runtime_sec: float = None
) -> None:
    """Save optimization results to a file (Excel or JSON) and create visualization"""
    
    base_results_dir = parameters.results_dir

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = '.xlsx' if format == 'excel' else '.json'
        output_filename = base_results_dir / f"optimization_results_{timestamp}{extension}"
    else:
        output_filename = Path(filename)
    
    output_filename.parent.mkdir(parents=True, exist_ok=True)

    # Calculate metrics and prepare data
    if 'Customers' in selected_clusters.columns:
        customers_per_cluster = selected_clusters['Customers'].apply(len)
    else:
        # For benchmark results, use Num_Customers column
        customers_per_cluster = selected_clusters['Num_Customers']
    
    # Calculate load percentages
    load_percentages = []
    for _, cluster in selected_clusters.iterrows():
        if 'Vehicle_Utilization' in cluster:
            total_utilization = cluster['Vehicle_Utilization']
        else:
            total_demand = ast.literal_eval(cluster['Total_Demand']) if isinstance(cluster['Total_Demand'], str) else cluster['Total_Demand']
            config = configurations_df[configurations_df['Config_ID'] == cluster['Config_ID']].iloc[0]
            total_utilization = (sum(total_demand.values()) / config['Capacity']) * 100
        
        load_percentages.append(total_utilization)
        logger.debug(f"Cluster {cluster['Cluster_ID']}: Load Percentage = {total_utilization}")
    
    load_percentages = pd.Series(load_percentages)
    
    summary_metrics = [
        ('Total Cost ($)', f"{total_fixed_cost + total_variable_cost + total_penalties:,.2f}"),
        ('Fixed Cost ($)', f"{total_fixed_cost:,.2f}"),
        ('Variable Cost ($)', f"{total_variable_cost:,.2f}"),
        ('Total Penalties ($)', f"{total_penalties:,.2f}"),
        ('  Light Load Penalties ($)', f"{total_light_load_penalties:,.2f}"),
        ('  Compartment Setup Penalties ($)', f"{total_compartment_penalties:,.2f}"),
        ('Total Vehicles', len(selected_clusters)),
    ]
    
    if expected_vehicles is not None:
        summary_metrics.append(('Expected Vehicles', expected_vehicles))
    
    for vehicle_type in sorted(vehicles_used.keys()):
        vehicle_count = vehicles_used[vehicle_type]
        summary_metrics.append(
            (f'Vehicles Type {vehicle_type}', vehicle_count)
        )
    
    summary_metrics.extend([
        ('Customers per Cluster (Min)', f"{customers_per_cluster.min():.0f}"),
        ('Customers per Cluster (Max)', f"{customers_per_cluster.max():.0f}"),
        ('Customers per Cluster (Avg)', f"{customers_per_cluster.mean():.1f}"),
        ('Customers per Cluster (Median)', f"{customers_per_cluster.median():.1f}"),
        ('Truck Load % (Min)', f"{load_percentages.min():.1f}"),
        ('Truck Load % (Max)', f"{load_percentages.max():.1f}"),
        ('Truck Load % (Avg)', f"{load_percentages.mean():.1f}"),
        ('Truck Load % (Median)', f"{load_percentages.median():.1f}"),
        ('---Parameters---', ''),
        ('Demand File', parameters.demand_file),
        ('Variable Cost per Hour', parameters.variable_cost_per_hour),
        ('Average Speed', parameters.avg_speed),
        ('Max Route Time', parameters.max_route_time),
        ('Service Time per Customer', parameters.service_time),
        ('Max Split Depth', parameters.clustering['max_depth']),
        ('Clustering Method', parameters.clustering['method']),
        ('Clustering Distance', parameters.clustering['distance']),
        ('Geography Weight', parameters.clustering['geo_weight']),
        ('Demand Weight', parameters.clustering['demand_weight']),
        ('Route Time Estimation Method', parameters.clustering['route_time_estimation']),
        ('Light Load Penalty', parameters.light_load_penalty),
        ('Light Load Threshold', parameters.light_load_threshold),
        ('Compartment Setup Cost', parameters.compartment_setup_cost)
        ])
    
    # Add vehicle types
    for v_type, specs in parameters.vehicles.items():
        for spec_name, value in specs.items():
            metric_name = f'Vehicle {v_type} {spec_name}'
            summary_metrics.append((metric_name, value))

    # Prepare cluster details
    cluster_details = selected_clusters.copy()
    if 'Customers' in cluster_details.columns:
        cluster_details['Num_Customers'] = cluster_details['Customers'].apply(len)
        cluster_details['Customers'] = cluster_details['Customers'].apply(str)
    if 'TSP_Sequence' in cluster_details.columns:
        cluster_details['TSP_Sequence'] = cluster_details['TSP_Sequence'].apply(
            lambda x: ' -> '.join(map(str, x)) if isinstance(x, (list, tuple)) and x else str(x)
        )
    if 'Total_Demand' in cluster_details.columns:
        cluster_details['Total_Demand'] = cluster_details['Total_Demand'].apply(str)
        
        # Add demand and load percentages by product type
        for cluster_idx, cluster in cluster_details.iterrows():
            config = configurations_df[
                configurations_df['Config_ID'] == cluster['Config_ID']
            ].iloc[0]
            
            total_demand = ast.literal_eval(cluster['Total_Demand']) if isinstance(cluster['Total_Demand'], str) else cluster['Total_Demand']
            total_demand_sum = sum(total_demand.values())
            
            # Calculate demand percentage for each product type first
            for good in parameters.goods:
                demand_column_name = f'Demand_{good}_pct'
                cluster_details.at[cluster_idx, demand_column_name] = (
                    total_demand[good] / total_demand_sum if total_demand_sum > 0 else 0
                )
            
            # Then calculate load percentage for each product type
            for good in parameters.goods:
                load_column_name = f'Load_{good}_pct'
                cluster_details.at[cluster_idx, load_column_name] = (
                    total_demand[good] / config['Capacity']
                )
            
            # Calculate TOTAL load percentage and empty percentage
            config_capacity = config['Capacity']
            total_load_pct = total_demand_sum / config_capacity if config_capacity > 0 else 0
            cluster_details.at[cluster_idx, 'Load_total_pct'] = total_load_pct
            cluster_details.at[cluster_idx, 'Load_empty_pct'] = 1 - total_load_pct

    data = {
        'summary_metrics': summary_metrics,
        'configurations_df': configurations_df,
        'cluster_details': cluster_details,
        'vehicles_used': vehicles_used,
        'other_considerations': [
            ('Total Vehicles Used', len(selected_clusters)),
            ('Number of Unserved Customers', len(missing_customers)),
            ('Unserved Customers', str(list(missing_customers)) if missing_customers else "None"),
            ('Average Customers per Cluster', cluster_details['Num_Customers'].mean() if 'Num_Customers' in cluster_details.columns else 'N/A'),
            ('Average Distance per Cluster', cluster_details['Estimated_Distance'].mean() if 'Estimated_Distance' in cluster_details.columns else 'N/A')
        ],
        'execution_details': [
            ('Execution Time (s)', execution_time),
            ('Solver', solver_name),
            ('Solver Status', solver_status),
            ('Solver Runtime (s)', solver_runtime_sec),
            ('Post-Optimization Runtime (s)', post_optimization_runtime_sec),
            ('Total Fixed Cost', total_fixed_cost),
            ('Total Variable Cost', total_variable_cost),
            ('Total Penalties', total_penalties),
            ('Light Load Penalties', total_light_load_penalties),
            ('Compartment Setup Penalties', total_compartment_penalties),
            ('Total Cost', total_fixed_cost + total_variable_cost + total_penalties),
            ('Demand File', parameters.demand_file)
        ]
    }

    try:
        if format == 'json':
            _write_to_json(output_filename, data)
        else:
            _write_to_excel(output_filename, data)
            
        # Only create visualization for optimization results
        if not is_benchmark:
            depot_coords = (parameters.depot['latitude'], parameters.depot['longitude'])
            visualize_clusters(selected_clusters, depot_coords, str(output_filename))
            
    except Exception as e:
        print(f"Error saving results to {output_filename}: {str(e)}")
        raise

def _write_to_excel(filename: str, data: dict) -> None:
    """Write optimization results to Excel file."""
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Sheet 1: Summary
        pd.DataFrame(data['summary_metrics'], columns=['Metric', 'Value']).to_excel(
            writer, sheet_name='Solution Summary', index=False
        )
        
        # Sheet 2: Configurations
        data['configurations_df'].to_excel(
            writer, sheet_name='Configurations', index=False
        )
        
        # Sheet 3: Selected Clusters
        cluster_cols = [col for col in data['cluster_details'].columns if col not in ['Customers', 'TSP_Sequence']] + ['Customers', 'TSP_Sequence']
        # Reorder cols to put Customers and TSP_Sequence last, if they exist
        cluster_cols_ordered = [col for col in cluster_cols if col in data['cluster_details'].columns]
        data['cluster_details'].to_excel(
            writer, sheet_name='Selected Clusters', index=False, columns=cluster_cols_ordered
        )
        
        # Sheet 4: Vehicle Usage
        vehicles_df = pd.DataFrame(
            [(k, v) for k, v in data['vehicles_used'].items()],
            columns=['Vehicle Type', 'Count']
        )
        vehicles_df.to_excel(writer, sheet_name='Vehicle Usage', index=False)
        
        # Sheet 5: Other Considerations
        pd.DataFrame(data['other_considerations'], columns=['Metric', 'Value']).to_excel(
            writer, sheet_name='Other Considerations', index=False
        )

        # Sheet 6: Execution Details
        pd.DataFrame(data['execution_details'], columns=['Metric', 'Value']).to_excel(
            writer, sheet_name='Execution Details', index=False
        )

def _write_to_json(filename: str, data: dict) -> None:
    """Write optimization results to JSON file."""
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            if isinstance(obj, (np.floating, np.float64)):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    # Convert vehicles_used to list of dictionaries
    # Ensure cluster details are serializable (TSP sequence might be list)
    serializable_clusters = data['cluster_details'].to_dict(orient='records')
    for cluster in serializable_clusters:
        if 'TSP_Sequence' in cluster and isinstance(cluster['TSP_Sequence'], list):
            cluster['TSP_Sequence'] = ' -> '.join(map(str, cluster['TSP_Sequence']))

    vehicle_usage = [
        {"vehicle_type": k, "count": v} 
        for k, v in data['vehicles_used'].items()
    ]

    json_data = {
        'Solution Summary': dict(data['summary_metrics']),
        'Configurations': data['configurations_df'].to_dict(orient='records'),
        'Selected Clusters': serializable_clusters, # Use serializable version
        'Vehicle Usage': vehicle_usage,
        'Other Considerations': dict(data['other_considerations']),
        'Execution Details': dict(data['execution_details'])
    }

    with open(filename, 'w') as f:
        json.dump(json_data, f, cls=NumpyEncoder, indent=2)

def visualize_clusters(
    selected_clusters: pd.DataFrame,
    depot_coords: tuple,
    filename: str
) -> None:
    """
    Create and save an interactive map visualization of the clusters in Bogotá.
    
    Args:
        selected_clusters: DataFrame containing cluster information
        depot_coords: Tuple of (latitude, longitude) coordinates for the depot
        filename: Base filename to save the plot (will append _clusters.html)
    """
    # Initialize the map centered on Bogotá
    m = folium.Map(
        location=[4.65, -74.1],  # Bogotá center
        zoom_start=11,
        tiles='CartoDB positron'
    )
    
    # Create color palette for clusters
    n_clusters = len(selected_clusters)
    colors = sns.color_palette("husl", n_colors=n_clusters).as_hex()
    
    # Add depot marker
    folium.Marker(
        location=depot_coords,
        icon=folium.Icon(color='red', icon='home', prefix='fa'),
        popup='Depot'
    ).add_to(m)
    
    # Plot each cluster
    for idx, (_, cluster) in enumerate(selected_clusters.iterrows()):
        color = colors[idx]
        cluster_id = cluster['Cluster_ID']
        config_id = cluster['Config_ID']
        
        # Calculate total demand in kg
        total_demand = sum(cluster['Total_Demand'].values()) if isinstance(cluster['Total_Demand'], dict) else 0
        if isinstance(cluster['Total_Demand'], str):
            total_demand = sum(ast.literal_eval(cluster['Total_Demand']).values())
        
        # Get number of customers
        num_customers = len(ast.literal_eval(cluster['Customers']) if isinstance(cluster['Customers'], str) else cluster['Customers'])
        
        # Prepare popup content with Method field
        popup_content = f"""
            <b>Cluster ID:</b> {cluster_id}<br>
            <b>Config ID:</b> {config_id}<br>
            <b>Method:</b> {cluster['Method']}<br>
            <b>Customers:</b> {num_customers}<br>
            <b>Route Time:</b> {cluster['Route_Time']:.2f} hrs<br>
            <b>Total Demand:</b> {total_demand:,.0f} kg
        """
        
        # Plot cluster centroid with larger circle
        folium.CircleMarker(
            location=(cluster['Centroid_Latitude'], cluster['Centroid_Longitude']),
            radius=8,
            color=color,
            fill=True,
            popup=folium.Popup(popup_content, max_width=300),
            weight=2,
            fill_opacity=0.7
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save map
    viz_filename = str(filename).rsplit('.', 1)[0] + '_clusters.html'
    m.save(viz_filename)

def save_benchmark_results(
    solutions: Dict[str, VRPSolution],
    parameters: Parameters,
    benchmark_type: BenchmarkType,
    filename: str = None,
    format: str = 'excel'
) -> None:
    """Save VRP benchmark results in the same format as optimization results"""
    
    # Calculate total metrics across all solutions
    total_cost = sum(sol.total_cost for sol in solutions.values())
    execution_time = max(sol.execution_time for sol in solutions.values())
    
    # Create configurations DataFrame
    configurations = []
    for vt_name, vt_info in parameters.vehicles.items():
        if benchmark_type == BenchmarkType.SINGLE_COMPARTMENT:
            for product in parameters.goods:
                configurations.append({
                    'Config_ID': f"{product}_{vt_name}",
                    'Vehicle_Type': vt_name,
                    'Capacity': vt_info['capacity'],
                    'Fixed_Cost': vt_info['fixed_cost'],
                    'Dry': 1 if product == 'Dry' else 0,
                    'Chilled': 1 if product == 'Chilled' else 0,
                    'Frozen': 1 if product == 'Frozen' else 0
                })
        else:  # MULTI_COMPARTMENT
            configurations.append({
                'Config_ID': f"mcv_{vt_name}",
                'Vehicle_Type': vt_name,
                'Capacity': vt_info['capacity'],
                'Fixed_Cost': vt_info['fixed_cost'],
                'Dry': 1,
                'Chilled': 1,
                'Frozen': 1
            })
    
    configurations_df = pd.DataFrame(configurations)
    
    # Create cluster details DataFrame from routes
    cluster_details = []
    for product, solution in solutions.items():
        for route_idx, route in enumerate(solution.routes):
            if route:  # Skip empty routes
                # Get vehicle type index from the route's vehicle type
                vehicle_type = list(parameters.vehicles.keys())[solution.vehicle_types[route_idx]]
                config_id = (
                    f"{product}_{vehicle_type}" if benchmark_type == BenchmarkType.SINGLE_COMPARTMENT 
                    else f"mcv_{vehicle_type}"
                )
                
                # Calculate actual utilization percentage
                vehicle_capacity = parameters.vehicles[vehicle_type]['capacity']
                utilization = solution.vehicle_loads[route_idx] / vehicle_capacity
                
                route_detail = {
                    'Cluster_ID': f"{product}_route_{route_idx}",
                    'Config_ID': config_id,
                    'Num_Customers': len(route) - 1,  # Subtract depot
                    'Route_Time': solution.route_times[route_idx],
                    'Estimated_Distance': solution.route_distances[route_idx],
                    'Vehicle_Utilization': utilization
                }
                
                if benchmark_type == BenchmarkType.SINGLE_COMPARTMENT:
                    # For single compartment, only one product has demand
                    for good in parameters.goods:
                        # Demand percentage is 100% for the product type, 0% for others
                        route_detail[f'Demand_{good}_pct'] = 1.0 if good == product else 0.0
                        # Load percentage is the vehicle utilization for the product type, 0% for others
                        route_detail[f'Load_{good}_pct'] = utilization if good == product else 0.0
                    
                    # Calculate empty percentage
                    route_detail['Load_empty_pct'] = 1.0 - utilization
                    route_detail['Vehicle_Utilization'] = utilization
                
                else:  # MULTI_COMPARTMENT
                    if hasattr(solution, 'compartment_configurations'):
                        config = solution.compartment_configurations[route_idx]
                        total_load = sum(config.values())
                        
                        # Set demand percentages based on compartment configuration
                        for good in parameters.goods:
                            route_detail[f'Demand_{good}_pct'] = config.get(good, 0.0) / total_load if total_load > 0 else 0.0
                            route_detail[f'Load_{good}_pct'] = config.get(good, 0.0)
                        
                        # Empty percentage is already calculated in the configuration
                        route_detail['Load_empty_pct'] = 1.0 - total_load
                        route_detail['Vehicle_Utilization'] = total_load

                
                cluster_details.append(route_detail)
    
    cluster_details = pd.DataFrame(cluster_details)
    
    # Count vehicles used by type
    vehicles_used = pd.Series({
        vt_name: sum(1 for sol in solutions.values() 
                    for vt_idx in sol.vehicle_types 
                    if list(parameters.vehicles.keys())[vt_idx] == vt_name)
        for vt_name in parameters.vehicles.keys()
    })
    
    # Call existing save function with data from solutions
    save_optimization_results(
        execution_time=execution_time,
        solver_name='PyVRP',
        solver_status='Optimal',
        configurations_df=configurations_df,
        selected_clusters=cluster_details,
        total_fixed_cost=sum(sol.fixed_cost for sol in solutions.values()),
        total_variable_cost=sum(sol.variable_cost for sol in solutions.values()),
        total_light_load_penalties=0,
        total_compartment_penalties=0,
        total_penalties=0,
        vehicles_used=vehicles_used,
        missing_customers=set(),
        parameters=parameters,
        filename=filename,
        format=format,
        is_benchmark=True
    )