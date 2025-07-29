"""
Main module for ldaputil package
"""

def greet(name="World"):
    """
    Greet someone with a hello message
    
    Args:
        name (str): Name to greet, defaults to "World"
        
    Returns:
        str: Greeting message
    """
    message = f"Hello {name} from ldaputil!"
    print(message)
    return message

def main():
    """Main entry point for the package"""
    print("ldaputil package is working correctly!")
    greet()

if __name__ == "__main__":
    main() 