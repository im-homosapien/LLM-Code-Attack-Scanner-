# scanner.py
# Simple lexical scanner to detect Level II Code Embedded Attacks

BAD_KEYWORDS = [
    "bomb", "hack", "counterfeit", "weapon", "drug", "illegal", "kill", 
    "poison", "jailbreak", "override", "ignore all", "developer mode"
]

def scan_code(code: str) -> dict:
    """
    Scans the code for suspicious Level II attack patterns.
    Returns: {'status': 'SAFE' or 'ATTACK', 'reason': 'explanation'}
    """
    
    lines = code.lower().split('\n')
    
    for i, line in enumerate(lines):
        # Rule 1: Multiple string concatenations (very common in Level II)
        if line.count('+') >= 2 and ('"' in line or "'" in line):
            return {
                "status": "ATTACK",
                "reason": f"Multiple string concatenations detected on line {i+1} (Level II style)"
            }
        
        # Rule 2: Dangerous keywords (even if split)
        for keyword in BAD_KEYWORDS:
            if keyword in line:
                return {
                    "status": "ATTACK",
                    "reason": f"Suspicious keyword '{keyword}' found on line {i+1}"
                }
        
        # Rule 3: Suspicious comments
        if "#" in line:
            comment = line.split("#")[1].strip()
            if any(word in comment for word in ["ignore", "developer", "complete the following", "jailbreak"]):
                return {
                    "status": "ATTACK",
                    "reason": f"Suspicious comment detected on line {i+1}"
                }
        
        # Rule 4: Suspicious variable or function names
        if any(suspicious in line for suspicious in ["make_harm", "produce_counter", "how_to", "create_bomb"]):
            return {
                "status": "ATTACK",
                "reason": f"Suspicious variable/function name on line {i+1}"
            }
    
    return {
        "status": "SAFE",
        "reason": "No Level II attack patterns detected"
    }


# Simple CLI to test
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()
    
    result = scan_code(code)
    print(f"{result['status']}: {result['reason']}")