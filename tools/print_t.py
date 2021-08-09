def print_t(log_class="LOG", tag="", printout=""):
    log_class = f"[ {log_class.upper()} ] "
    if tag != "": 
        tag += " - "
        
    print(f"{log_class:>11}{tag}{printout}")
    
if __name__ == '__main__':
    print_t('ERROR', 'tag_name', 'Please write here.')