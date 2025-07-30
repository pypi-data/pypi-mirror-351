import traceback
from IPython.display import display, HTML
import os
import re

import ipywidgets as widgets
from IPython.core import ultratb
from ipykernel.comm import Comm
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

AI_MODEL = os.environ.get("CALLIOPE_ERROR_MODEL", "gpto")

def custom_exc(shell, etype, evalue, tb, tb_offset=None):
    error_message = str(evalue)
    error_type = etype.__name__    
    error_line = None
    try:
        for frame in traceback.extract_tb(tb):
            if frame.filename.startswith('<ipython-input-'):
                error_line = frame.lineno
                break
    except:
        pass
    
    current_cell = shell.user_ns.get('_ih', [""])[len(shell.user_ns.get('_ih', [""])) - 1]
    
    display(HTML(f"""
        <div style="background-color: #f8d7da; color: #721c24; padding: 15px; border: 1px solid #f5c6cb; border-radius: 5px; margin: 10px 0;">
            <h3 style="margin-top: 0;">{error_type} Error Detected</h3>
            <p><strong>Error:</strong> {error_message}</p>
            <p><strong>Line:</strong> {error_line if error_line is not None else 'unknown'}</p>
        </div>
    """))

    button_style = widgets.ButtonStyle(
        button_color='#3FF1EF',
        text_color='#161D2C'
    )

    fix_button = widgets.Button(
        description="Fix with Calliope",
        tooltip='Get AI to fix your code',
        icon='check',
        style=button_style
    )
    
    show_error_button = widgets.Button(
        description="Show Traceback",
        tooltip='Show the full error traceback',
        icon='bug',
        style=button_style
    )
    
    button_container = widgets.HBox([fix_button, show_error_button])
    display(button_container)
    
    output_area = widgets.Output()
    display(output_area)

    def on_fix_click(b):
        with output_area:
            output_area.clear_output()
            Comm(target_name='toggle_fixing').send({})
            display(HTML("""
            <div style="padding: 10px; margin: 5px 0; display: flex; align-items: center;">
                <span>Calliope is fixing your code, please wait...</span>
            </div>
            """))
            
            # Prepare the prompt as a properly escaped string literal
            # Double all curly braces in the code to escape them in the f-string
            code_with_error = current_cell.replace('{', '{{').replace('}', '}}')
            
            # Create the prompt as a regular string, not an f-string for the code part
            ai_prompt = f"""
Please fix the following Python code that resulted in a {error_type} error: {error_message}

---CODE WITH ERROR---
{code_with_error}
---END CODE---

Provide ONLY the fixed code without any explanations or markdown formatting. The error occurred on line {error_line if error_line is not None else 'unknown'}.
"""
            
            # Create the magic command
            ai_magic = f"%%ai {AI_MODEL}\n{ai_prompt}"
            
            try:
                res = shell.run_cell(ai_magic)
                fixed_code = None
                
                if hasattr(res.result, '_repr_markdown_'):
                    markdown_content = res.result._repr_markdown_()
                    code_blocks = re.findall(r'```(?:python)?\n(.*?)```', markdown_content[0], re.DOTALL)
                    if code_blocks:
                        fixed_code = code_blocks[0].strip()
                    else:
                        fixed_code = markdown_content.strip()
    
                output_area.clear_output()
    
                Comm(target_name='toggle_fixing').send({})
                if fixed_code:
                    apply_fix_button = widgets.Button(
                        description="Apply Fix",
                        tooltip='Apply the fixed code to your cell',
                        icon='check-circle',
                        style=button_style
                    )
                    
                    apply_new_cell_button = widgets.Button(
                        description="New Cell",
                        tooltip='Apply the fixed code to a new cell',
                        icon='plus-square',
                        style=button_style
                    )
                    
                    display(HTML(f"""
                    <div style="padding: 15px; margin: 10px 0;">
                        <h3 style="margin-top: 0;">Fix Generated</h3>
                        <p>A fix has been generated. Choose how to apply it:</p>
                    </div>
                    """))
                    
                    # Create a styled code preview with Python syntax highlighting using Pygments
                    formatter = HtmlFormatter(style='rrt')
                    highlighted_code = highlight(fixed_code, PythonLexer(), formatter)
                    
                    code_html = f'''
                    <style>
                    {formatter.get_style_defs('.highlight')}
                    .highlight {{ padding: 12px; border-radius: 5px; }}
                    </style>
                    {highlighted_code}
                    '''
                    
                    preview_accordion = widgets.Accordion(children=[widgets.HTML(value=code_html)])
                    preview_accordion.set_title(0, 'Preview Fixed Code')
                                    
                    display(preview_accordion)
                    
                    button_container = widgets.HBox([apply_fix_button, apply_new_cell_button])
                    display(button_container)
                    
                    def on_apply_fix(b):
                        with output_area:
                            output_area.clear_output()                        
                            comm = Comm(target_name='replace_cell')
                            comm.send({'replace_with': fixed_code, 'execute_cell': True})
                    
                    def on_apply_new_cell(b):
                        with output_area:
                            output_area.clear_output()                        
                            comm = Comm(target_name='insert_new_cell')
                            comm.send({'cell_content': fixed_code, 'execute_cell': True})
                            
                    apply_fix_button.on_click(on_apply_fix)
                    apply_new_cell_button.on_click(on_apply_new_cell)
                else:
                    display(HTML(f"""
                    <div style="background-color: #172134; color: #BA2121; padding: 15px; margin: 10px 0;">
                        <h3 style="margin-top: 0;">Unable to Fix</h3>
                        <p>Calliope was unable to generate fixed code automatically.</p>
                    </div>
                    """))
            except Exception as e:
                output_area.clear_output()
                display(HTML(f"""
                <div style="background-color: #172134; color: #BA2121; padding: 15px; margin: 10px 0;">
                    <h3 style="margin-top: 0;">Error Processing Request</h3>
                    <p>An error occurred while processing your fix request: {str(e)}</p>
                </div>
                """))

    def on_show_error_click(b):
        with output_area:
            output_area.clear_output()
            formatter = ultratb.FormattedTB(mode='Context', color_scheme='Linux')
            formatted_tb = formatter.text(etype, evalue, tb)
            
            display(HTML(f"""
            <div style="padding: 15px; margin: 10px 0;">
                <h3 style="margin-top: 0;">Error Traceback:</h3>
                <pre style="padding: 10px; overflow: auto; white-space: pre-wrap;">{formatted_tb.replace('<', '&lt;').replace('>', '&gt;')}</pre>
            </div>
            """))

    fix_button.on_click(on_fix_click)
    show_error_button.on_click(on_show_error_click)

    return None

def load_ipython_extension(ipython):
    ipython.set_custom_exc((Exception,), custom_exc)

def unload_ipython_extension(ipython):
    ipython.set_custom_exc((), None)