"""
Script to fix deprecation warnings by patching the problematic modules.
"""
import sys
import os
import ast
import importlib
import types

def patch_reportlab():
    """
    Fix the ast.NameConstant deprecation in reportlab.
    """
    try:
        import reportlab.lib.rl_safe_eval as rl_safe_eval
        
        # Create a patched version of the module
        if hasattr(rl_safe_eval, 'haveNameConstant'):
            print("Patching reportlab.lib.rl_safe_eval...")
            
            # Modify the module's source code
            source_path = rl_safe_eval.__file__
            with open(source_path, 'r') as f:
                content = f.read()
            
            # Replace the problematic line
            if 'haveNameConstant = hasattr(ast,\'NameConstant\')' in content:
                content = content.replace(
                    'haveNameConstant = hasattr(ast,\'NameConstant\')',
                    'haveNameConstant = False  # Patched to avoid deprecation warning'
                )
                
                # Write the patched version back
                with open(source_path, 'w') as f:
                    f.write(content)
                print("Successfully patched reportlab.lib.rl_safe_eval")
            else:
                print("Could not find the exact line to patch in reportlab")
    except ImportError:
        print("reportlab module not found")
    except Exception as e:
        print(f"Error patching reportlab: {e}")

def identify_load_module_usage():
    """
    Identify modules using the deprecated load_module method.
    """
    print("Checking for modules using deprecated load_module()...")
    # This is harder to fix automatically as it could be in various places
    # We'll just report it for manual inspection
    
    # Check common modules that might use load_module
    modules_to_check = [
        'importlib',
        'pkg_resources',
        'setuptools',
        'pytest'
    ]
    
    for module_name in modules_to_check:
        try:
            module = importlib.import_module(module_name)
            print(f"Checking {module_name} at {getattr(module, '__file__', 'unknown location')}")
        except ImportError:
            print(f"Module {module_name} not found")
    
    print("\nTo fix load_module warnings, you may need to update the following packages:")
    print("pip install --upgrade setuptools pytest")

if __name__ == "__main__":
    print("Starting deprecation warning fixes...")
    patch_reportlab()
    identify_load_module_usage()
    print("\nDone. Please run your tests again to see if warnings are reduced.")
