import matplotlib.pyplot as plt
import numpy as np
import re
from collections import defaultdict

def parse_log_file(file_path):
    temperatures = []
    penalties = []
    operation_types = []
    hard_penalties = {'H1': [], 'H2': [], 'H3': [], 'H4': []}
    soft_penalties = {'S1': [], 'S2+S3+S5': [], 'S4': [], 'ComC': []}
    accepted_count = 0
    current_temp = None
    current_week = 0
    temp_iter = 0  # Track temperature iterations
    inner_iter = 0  # Track inner iterations within each temperature
    week_data = defaultdict(lambda: {
        'temperatures': [],
        'penalties': [],
        'hard_penalties': [],
        'soft_penalties': [],
        'comc_penalties': [],
        'temp_iterations': [],  # Store temperature iteration numbers
        'inner_iterations': []  # Store inner iteration numbers
    })
    
    with open(file_path, 'r') as f:
        for line in f:
            # Parse temperature and week
            if 'Current temperature:' in line:
                current_temp = float(line.split('Current temperature:')[1].split(',')[0].strip())
                temperatures.append(current_temp)
                week_data[current_week]['temperatures'].append(current_temp)
                temp_iter += 1
                inner_iter = 0  # Reset inner iteration counter for new temperature
            
            # Parse penalties
            if 'penalties' in line and '--' in line:
                parts = line.split('--')
                total_penalty = float(parts[0].split('penalties')[1].strip())
                penalties.append(total_penalty)
                week_data[current_week]['penalties'].append(total_penalty)
                week_data[current_week]['temp_iterations'].append(temp_iter)
                week_data[current_week]['inner_iterations'].append(inner_iter)
                
                # Parse detailed penalties
                details = parts[1].strip()
                hard_total = 0
                soft_total = 0
                comc = 0
                
                for h in ['H1', 'H2', 'H3', 'H4']:
                    match = re.search(f'{h}: (\d+)', details)
                    if match:
                        hard_penalties[h].append(float(match.group(1)))
                        hard_total += float(match.group(1))
                
                for s in ['S1', 'S2+S3+S5', 'S4']:
                    match = re.search(f'{s}: ([\d.]+)', details)
                    if match:
                        soft_penalties[s].append(float(match.group(1)))
                        soft_total += float(match.group(1))
                
                comc_match = re.search(f'ComC: ([\d.]+)', details)
                if comc_match:
                    comc = float(comc_match.group(1))
                    soft_penalties['ComC'].append(comc)
                
                week_data[current_week]['hard_penalties'].append(hard_total)
                week_data[current_week]['soft_penalties'].append(soft_total)
                week_data[current_week]['comc_penalties'].append(comc)
                inner_iter += 1
            
            # Parse operation type
            if any(op in line for op in ['multi_changing', 'multi_swaping', 'double_changing']):
                for op in ['multi_changing', 'multi_swaping', 'double_changing']:
                    if op in line:
                        operation_types.append(op)
                        break
            
            # Count accepted moves
            if 'Accepted:' in line:
                accepted_count += 1
            
            # Check for week change
            if '--- Temperature Level' in line:
                current_week += 1
                temp_iter = 0  # Reset temperature iteration counter for new week
                inner_iter = 0  # Reset inner iteration counter for new week
    
    return {
        'temperatures': temperatures,
        'penalties': penalties,
        'operation_types': operation_types,
        'hard_penalties': hard_penalties,
        'soft_penalties': soft_penalties,
        'accepted_count': accepted_count,
        'week_data': week_data
    }

def plot_temperature_penalty(data):
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Plot temperature with thinner line
    ax1.plot(data['temperatures'], 'r-', label='Temperature', linewidth=0.8)
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Temperature', color='r')
    ax1.tick_params(axis='y', labelcolor='r')
    ax1.grid(True, alpha=0.3)
    
    # Plot penalty on secondary y-axis with thinner line
    ax2 = ax1.twinx()
    ax2.plot(data['penalties'], 'b-', label='Total Penalty', linewidth=0.8)
    ax2.set_ylabel('Total Penalty', color='b')
    ax2.tick_params(axis='y', labelcolor='b')
    
    # Add legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    plt.title('Temperature and Penalty Changes')
    plt.tight_layout()
    plt.savefig('temperature_penalty.png')
    plt.close()

def plot_weekly_penalties(data):
    """Plot weekly penalties with separate subplots for each week"""
    # Create 2x2 grid for 4 weeks
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    axes = axes.flatten()
    
    # Create color scheme
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Blue, Orange, Green
    
    for week, ax in enumerate(axes):
        week_info = data['week_data'][week]
        temp_iterations = week_info['temp_iterations']
        inner_iterations = week_info['inner_iterations']
        total_iterations = [t * 20000 + i for t, i in zip(temp_iterations, inner_iterations)]
        
        # Plot each type of penalty with thinner lines
        ax.plot(total_iterations, week_info['hard_penalties'], 
               color=colors[0], linestyle='-', 
               label='Hard Constraints', linewidth=0.8)
        ax.plot(total_iterations, week_info['soft_penalties'], 
               color=colors[1], linestyle='-', 
               label='Soft Constraints', linewidth=0.8)
        ax.plot(total_iterations, week_info['comc_penalties'], 
               color=colors[2], linestyle='-', 
               label='ComC', linewidth=0.8)
        
        ax.set_title(f'Week {week}')
        ax.set_xlabel('Total Iterations')
        ax.set_ylabel('Penalty Value')
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    plt.tight_layout()
    plt.savefig('weekly_penalties.png', bbox_inches='tight', dpi=150)
    plt.close()

def plot_weekly_iterations_penalties(data):
    """Plot penalties vs iterations for each week in a single plot"""
    plt.figure(figsize=(12, 7))
    
    # Create color scheme
    cmap = plt.cm.get_cmap('tab10')  # Get a colormap for different weeks
    
    for week in range(4):  # For 4 weeks
        week_info = data['week_data'][week]
        temp_iterations = week_info['temp_iterations']
        inner_iterations = week_info['inner_iterations']
        total_iterations = [t * 20000 + i for t, i in zip(temp_iterations, inner_iterations)]
        
        plt.plot(
            total_iterations,
            week_info['penalties'],
            marker='o',
            markersize=3,
            linewidth=1,
            alpha=0.5,
            label=f'Week {week}',
            color=cmap(week)
        )
    
    plt.xlabel('Iterations')
    plt.ylabel('Penalty')
    plt.title('Penalties vs Iterations for Each Week')
    plt.grid(True, alpha=0.3)
    plt.legend(title='Week')
    plt.tight_layout()
    plt.savefig('weekly_iterations_penalties.png', dpi=300)
    plt.close()

def main():
    log_file = 'logs-comc100_0508/n030w4/scheduler_ComCw100_run2_20250508_073350.txt'
    data = parse_log_file(log_file)
    
    # Generate three separate plots
    plot_temperature_penalty(data)
    plot_weekly_penalties(data)
    plot_weekly_iterations_penalties(data)
    
    print(f"Total accepted moves: {data['accepted_count']}")
    print(f"Final temperature: {data['temperatures'][-1]}")
    print(f"Final penalty: {data['penalties'][-1]}")

if __name__ == "__main__":
    main() 