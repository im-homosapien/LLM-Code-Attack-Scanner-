import os
from scanner import scan_code

VALID_EXTENSIONS = {'.py', '.js', '.java', '.go', '.cpp', '.c', '.txt'}


def read_file(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def collect_files(folder: str):
    files = []
    if not os.path.exists(folder):
        return files

    for root, _, filenames in os.walk(folder):
        for name in filenames:
            _, ext = os.path.splitext(name)
            if ext.lower() in VALID_EXTENSIONS:
                files.append(os.path.join(root, name))

    return sorted(files)


def evaluate_results(results):
    tp = sum(1 for r in results if r['true_label'] == 'ATTACK' and r['detected_label'] == 'ATTACK')
    tn = sum(1 for r in results if r['true_label'] == 'SAFE' and r['detected_label'] == 'SAFE')
    fp = sum(1 for r in results if r['true_label'] == 'SAFE' and r['detected_label'] == 'ATTACK')
    fn = sum(1 for r in results if r['true_label'] == 'ATTACK' and r['detected_label'] == 'SAFE')

    total = len(results)
    accuracy = (tp + tn) / total if total else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return {
        'total': total,
        'tp': tp,
        'tn': tn,
        'fp': fp,
        'fn': fn,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
    }


def scan_folder(folder: str, true_label: str):
    results = []
    files = collect_files(folder)

    for filepath in files:
        code = read_file(filepath)
        result = scan_code(code)
        detected_label = result['status']
        reason = result['reason']

        results.append({
            'file': filepath,
            'true_label': true_label,
            'detected_label': detected_label,
            'reason': reason,
            'correct': detected_label == true_label,
        })

    return results


def print_file_results(results):
    print('=== File Scan Results ===')
    for r in results:
        print(f"{r['file']}")
        print(f"  True label    : {r['true_label']}")
        print(f"  Scanner result: {r['detected_label']}")
        print(f"  Correct       : {r['correct']}")
        print(f"  Reason        : {r['reason']}")
        print()


def print_evaluation(metrics):
    print('=== Evaluation ===')
    print(f"Total files : {metrics['total']}")
    print(f"TP          : {metrics['tp']}")
    print(f"TN          : {metrics['tn']}")
    print(f"FP          : {metrics['fp']}")
    print(f"FN          : {metrics['fn']}")
    print(f"Accuracy    : {metrics['accuracy']:.2%}")
    print(f"Precision   : {metrics['precision']:.2%}")
    print(f"Recall      : {metrics['recall']:.2%}")
    print(f"F1 Score    : {metrics['f1']:.2%}")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    attack_dir = os.path.join(base_dir, 'attacks')
    safe_dir = os.path.join(base_dir, 'safe')

    attack_results = scan_folder(attack_dir, 'ATTACK')
    safe_results = scan_folder(safe_dir, 'SAFE')

    all_results = attack_results + safe_results

    if not all_results:
        print("No files found. Make sure 'attacks/' and 'safe/' folders exist and contain test files.")
        return

    print_file_results(all_results)
    metrics = evaluate_results(all_results)
    print_evaluation(metrics)


if __name__ == '__main__':
    main()
