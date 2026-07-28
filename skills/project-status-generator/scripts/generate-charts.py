#!/usr/bin/env python3
"""
Generate project status charts from task data.

Usage:
    python generate-charts.py <data-json> <output-dir>

Data JSON format:
{
    "title": "Project Name",
    "date": "03-13",
    "milestones": [
        {
            "name": "M1: Add Nodes",
            "percent": 99,
            "deadline": "02-28",
            "deadline_status": "done",  # done | past_due | upcoming | tbd
            "tasks": [
                {"name": "Task Name", "status": "done", "owner": "Person"}
            ]
        }
    ]
}

Status values: done, in_progress, in_review, needs_discussion, not_started, punted, duplicate, paused
"""

import json
import sys
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Dark theme colors
BG_COLOR = '#1e1e2e'
TEXT_COLOR = '#ffffff'
GRID_COLOR = '#333355'

STATUS_COLORS = {
    'done': '#4ade80',
    'in_progress': '#60a5fa',
    'in_review': '#a78bfa',
    'needs_discussion': '#fbbf24',
    'not_started': '#6b7280',
    'punted': '#f87171',
    'duplicate': '#9ca3af',
    'paused': '#fb923c',
}

STATUS_LABELS = {
    'done': 'Done',
    'in_progress': 'In Progress',
    'in_review': 'In Review',
    'needs_discussion': 'Needs Discussion',
    'not_started': 'Not Started',
    'punted': 'Punt to M3',
    'duplicate': 'Duplicate',
    'paused': 'Paused',
}

DEADLINE_LABELS = {
    'done': '✅',
    'past_due': '❌ PAST DUE',
    'upcoming': '',
    'tbd': 'TBD',
}


def setup_style():
    plt.rcParams.update({
        'figure.facecolor': BG_COLOR,
        'axes.facecolor': BG_COLOR,
        'text.color': TEXT_COLOR,
        'axes.labelcolor': TEXT_COLOR,
        'xtick.color': TEXT_COLOR,
        'ytick.color': TEXT_COLOR,
        'axes.edgecolor': GRID_COLOR,
        'grid.color': GRID_COLOR,
        'font.family': 'sans-serif',
        'font.size': 11,
    })


def generate_pie(milestone, output_dir):
    """Generate pie chart for a single milestone's task status distribution."""
    status_counts = {}
    for task in milestone['tasks']:
        s = task['status']
        status_counts[s] = status_counts.get(s, 0) + 1

    if not status_counts:
        return

    labels = [f"{STATUS_LABELS.get(s, s)} ({c})" for s, c in status_counts.items()]
    sizes = list(status_counts.values())
    colors = [STATUS_COLORS.get(s, '#6b7280') for s in status_counts.keys()]

    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct='%1.0f%%',
        startangle=90, pctdistance=0.6,
        wedgeprops={'linewidth': 2, 'edgecolor': BG_COLOR}
    )
    for t in texts:
        t.set_color(TEXT_COLOR)
        t.set_fontsize(10)
    for t in autotexts:
        t.set_color(TEXT_COLOR)
        t.set_fontweight('bold')
        t.set_fontsize(11)

    safe_name = milestone['name'].lower().replace(' ', '-').replace(':', '').replace('+', '')[:30]
    ax.set_title(f"{milestone['name']} — Task Status", fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{safe_name}-pie.png"), dpi=150, bbox_inches='tight')
    plt.close()


def generate_gantt(milestone, output_dir):
    """Generate horizontal bar chart of tasks by status and owner."""
    tasks = milestone['tasks']
    if not tasks:
        return

    names = [f"{t['name']} ({t.get('owner', '?')})" for t in tasks]
    colors = [STATUS_COLORS.get(t['status'], '#6b7280') for t in tasks]

    # Sort by status
    status_order = ['done', 'in_review', 'in_progress', 'needs_discussion', 'paused', 'not_started', 'punted', 'duplicate']
    indexed = list(zip(names, colors, [status_order.index(t['status']) if t['status'] in status_order else 99 for t in tasks]))
    indexed.sort(key=lambda x: x[2], reverse=True)
    names = [x[0] for x in indexed]
    colors = [x[1] for x in indexed]

    fig, ax = plt.subplots(figsize=(12, max(4, len(tasks) * 0.4)), dpi=150)
    y_pos = range(len(names))
    ax.barh(y_pos, [1] * len(names), color=colors, height=0.7, edgecolor=BG_COLOR, linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xticks([])
    ax.set_xlim(0, 1.2)

    # Legend
    seen = set()
    patches = []
    for t in tasks:
        s = t['status']
        if s not in seen:
            seen.add(s)
            patches.append(mpatches.Patch(color=STATUS_COLORS.get(s, '#6b7280'), label=STATUS_LABELS.get(s, s)))
    ax.legend(handles=patches, loc='lower right', fontsize=8, facecolor=BG_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)

    safe_name = milestone['name'].lower().replace(' ', '-').replace(':', '').replace('+', '')[:30]
    ax.set_title(f"{milestone['name']} — Tasks by Owner", fontsize=13, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{safe_name}-gantt.png"), dpi=150, bbox_inches='tight')
    plt.close()


def generate_milestones_overview(milestones, output_dir):
    """Generate milestone comparison chart with progress bars."""
    fig, ax = plt.subplots(figsize=(10, max(3, len(milestones) * 1.2)), dpi=150)

    names = [m['name'] for m in milestones]
    percents = [m['percent'] for m in milestones]
    remaining = [100 - p for p in percents]

    y_pos = range(len(names))
    ax.barh(y_pos, percents, color='#4ade80', height=0.5, label='Complete')
    ax.barh(y_pos, remaining, left=percents, color='#334155', height=0.5, label='Remaining')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=12, fontweight='bold')
    ax.set_xlim(0, 120)
    ax.set_xlabel('% Complete', fontsize=11)

    for i, m in enumerate(milestones):
        pct = m['percent']
        dl = m.get('deadline', 'TBD')
        ds = m.get('deadline_status', 'tbd')
        suffix = DEADLINE_LABELS.get(ds, '')
        label = f"{pct}%   {dl} {suffix}"
        ax.text(pct + 2, i, label, va='center', fontsize=10, color=TEXT_COLOR, fontweight='bold')

    ax.set_title("Milestone Progress", fontsize=14, fontweight='bold', pad=15)
    ax.legend(loc='lower right', fontsize=9, facecolor=BG_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'milestones-overview.png'), dpi=150, bbox_inches='tight')
    plt.close()


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <data.json> <output-dir>", file=sys.stderr)
        sys.exit(1)

    data_path = sys.argv[1]
    output_dir = sys.argv[2]

    with open(data_path) as f:
        data = json.load(f)

    os.makedirs(output_dir, exist_ok=True)
    setup_style()

    for milestone in data['milestones']:
        generate_pie(milestone, output_dir)
        generate_gantt(milestone, output_dir)

    generate_milestones_overview(data['milestones'], output_dir)

    print(f"Charts generated in {output_dir}/", file=sys.stderr)
    for f in sorted(os.listdir(output_dir)):
        if f.endswith('.png'):
            print(os.path.join(output_dir, f))


if __name__ == '__main__':
    main()
