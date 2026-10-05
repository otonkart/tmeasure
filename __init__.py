bl_info = {
    "name": "tmeasure",
    "author": "Otonkart",
    "version": (1, 1, 3),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar (N) > Measure > tmeasure",
    "description": "Smart edge/face measurement + dimensions + scale fix + clipboard",
    "category": "Mesh",
}

import bpy
import bmesh

# --- Core measurement ---
def get_selected_measurement(context):
    obj = context.edit_object
    if not obj or obj.type != 'MESH':
        return 0.0, False

    bm = bmesh.from_edit_mesh(obj.data)
    sel_mode = context.tool_settings.mesh_select_mode
    is_area = sel_mode[2]  # True if Face select mode is active

    total = 0.0
    if is_area:
        for f in bm.faces:
            if f.select:
                total += f.calc_area()
    else:
        for e in bm.edges:
            if e.select:
                total += e.calc_length()
                
    return total, is_area

# --- Unit formatting ---
def format_measurement(value_in_meters: float, unit: str, is_area: bool = False):
    if is_area:
        if unit == 'CM': return value_in_meters * 10000.0, "cm²"
        if unit == 'MM': return value_in_meters * 1000000.0, "mm²"
        if unit == 'FT': return value_in_meters * 10.7639, "sq ft"
        if unit == 'IN': return value_in_meters * 1550.003, "sq in"
        return value_in_meters, "m²"
    else:
        if unit == 'CM': return value_in_meters * 100.0, "cm"
        if unit == 'MM': return value_in_meters * 1000.0, "mm"
        if unit == 'FT': return value_in_meters * 3.28084, "ft"
        if unit == 'IN': return value_in_meters * 39.3701, "in"
        return value_in_meters, "m"

def is_scale_applied(obj, eps=1e-6):
    if not obj:
        return True
    s = obj.scale
    return (abs(s.x - 1.0) < eps) and (abs(s.y - 1.0) < eps) and (abs(s.z - 1.0) < eps)

# --- Property Group ---
class TMeasureHistoryItem(bpy.types.PropertyGroup):
    obj_name: bpy.props.StringProperty(name="Object Name")
    value: bpy.props.FloatProperty(name="Value", default=0.0, precision=6)
    is_area: bpy.props.BoolProperty(name="Is Area", default=False)

# --- Operators ---
class OBJECT_OT_tmeasure_apply_scale(bpy.types.Operator):
    """Apply scale to the active object (Ctrl+A)"""
    bl_idname = "object.tmeasure_apply_scale"
    bl_label = "Apply Scale"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if obj:
            current_mode = context.mode
            if current_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            
            if current_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode=current_mode)
                
            self.report({'INFO'}, "Scale applied successfully.")
        return {'FINISHED'}

class MESH_OT_tmeasure_calculate(bpy.types.Operator):
    """Calculate total length or area based on selection mode"""
    bl_idname = "mesh.tmeasure_calculate"
    bl_label = "Calculate Selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.mode != 'EDIT_MESH':
            self.report({'WARNING'}, "Mesh Edit Mode gerekli.")
            return {'CANCELLED'}

        obj = context.edit_object
        total, is_area = get_selected_measurement(context)
        
        # Update Scene Properties
        context.scene.tmeasure_last_value = total
        context.scene.tmeasure_last_is_area = is_area
        context.scene.tmeasure_last_obj_name = obj.name

        # Update History
        hist = context.scene.tmeasure_history
        item = hist.add()
        item.obj_name = obj.name
        item.value = total
        item.is_area = is_area

        while len(hist) > 5:
            hist.remove(0)

        disp_val, disp_unit = format_measurement(total, context.scene.tmeasure_unit, is_area)
        meas_type = "Area" if is_area else "Length"
        self.report({'INFO'}, f"{meas_type}: {disp_val:.4f} {disp_unit}")
        return {'FINISHED'}

class MESH_OT_tmeasure_clear_history(bpy.types.Operator):
    """Clear last measurements history"""
    bl_idname = "mesh.tmeasure_clear_history"
    bl_label = "Clear History"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.tmeasure_history.clear()
        self.report({'INFO'}, "History cleared.")
        return {'FINISHED'}

class UI_OT_tmeasure_copy_clipboard(bpy.types.Operator):
    """Copy the last calculated measurement to clipboard"""
    bl_idname = "ui.tmeasure_copy_clipboard"
    bl_label = "Copy to Clipboard"

    def execute(self, context):
        val = context.scene.tmeasure_last_value
        is_area = context.scene.tmeasure_last_is_area
        unit = context.scene.tmeasure_unit
        
        disp_val, disp_unit = format_measurement(val, unit, is_area)
        copy_text = f"{disp_val:.4f} {disp_unit}"
        
        context.window_manager.clipboard = copy_text
        self.report({'INFO'}, f"Copied: {copy_text}")
        return {'FINISHED'}

# --- UI Panel ---
class VIEW3D_PT_tmeasure(bpy.types.Panel):
    bl_label = "tmeasure"
    bl_idname = "VIEW3D_PT_tmeasure"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TMeasure"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        
        # Object Dimensions
        col.label(text="Object Dimensions")
        obj = context.active_object
        
        if obj and obj.type == 'MESH':
            box = col.box()
            unit = context.scene.tmeasure_unit
            x_val, u = format_measurement(obj.dimensions.x, unit, False)
            y_val, _ = format_measurement(obj.dimensions.y, unit, False)
            z_val, _ = format_measurement(obj.dimensions.z, unit, False)
            
            row = box.row(align=True)
            row.label(text=f"X: {x_val:.4f} {u}")
            row.label(text=f"Y: {y_val:.4f} {u}")
            row.label(text=f"Z: {z_val:.4f} {u}")
            
            if not is_scale_applied(obj):
                col.separator()
                error_box = col.box()
                error_box.alert = True
                row = error_box.row(align=True)
                row.label(text="Scale not applied!", icon='ERROR')
                row.operator("object.tmeasure_apply_scale", text="Apply Scale", icon='CHECKMARK')
        else:
            col.label(text="(No Mesh Object Selected)", icon='INFO')

        col.separator()
        
        # Measurement Section
        col.label(text="Calculate (Edge Length / Face Area)")
        row = col.row(align=True)
        row.operator("mesh.tmeasure_calculate", text="Calculate", icon='DRIVER_DISTANCE')
        row.operator("mesh.tmeasure_clear_history", text="", icon='TRASH')

        col.separator()
        col.prop(context.scene, "tmeasure_unit", text="Unit")

        # Last Total & Copy
        last_val = context.scene.tmeasure_last_value
        last_is_area = context.scene.tmeasure_last_is_area
        disp_val, disp_unit = format_measurement(last_val, context.scene.tmeasure_unit, last_is_area)
        
        row_copy = col.row(align=True)
        row_copy.label(text=f"Last Total: {disp_val:.4f} {disp_unit}")
        row_copy.operator("ui.tmeasure_copy_clipboard", text="", icon='COPYDOWN')

        col.separator()
        
        # History
        col.label(text="Last 5 Measurements:")
        hist = context.scene.tmeasure_history
        if len(hist) == 0:
            col.label(text="(empty)")
        else:
            for i, it in enumerate(reversed(hist), start=1):
                v, u = format_measurement(it.value, context.scene.tmeasure_unit, it.is_area)
                name_lbl = it.obj_name if it.obj_name else "Unknown"
                col.label(text=f"{i}) {name_lbl}: {v:.4f} {u}")

classes = (
    TMeasureHistoryItem,
    OBJECT_OT_tmeasure_apply_scale,
    MESH_OT_tmeasure_calculate,
    MESH_OT_tmeasure_clear_history,
    UI_OT_tmeasure_copy_clipboard,
    VIEW3D_PT_tmeasure,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.tmeasure_last_value = bpy.props.FloatProperty(default=0.0, precision=6)
    bpy.types.Scene.tmeasure_last_is_area = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.tmeasure_last_obj_name = bpy.props.StringProperty(default="")
    
    bpy.types.Scene.tmeasure_history = bpy.props.CollectionProperty(type=TMeasureHistoryItem)
    bpy.types.Scene.tmeasure_unit = bpy.props.EnumProperty(
        name="Unit",
        items=[
            ('M', "m", "Meters"),
            ('CM', "cm", "Centimeters"),
            ('MM', "mm", "Millimeters"),
            ('FT', "ft", "Feet"),
            ('IN', "in", "Inches")
        ],
        default='M'
    )

def unregister():
    del bpy.types.Scene.tmeasure_unit
    del bpy.types.Scene.tmeasure_history
    del bpy.types.Scene.tmeasure_last_value
    del bpy.types.Scene.tmeasure_last_is_area
    del bpy.types.Scene.tmeasure_last_obj_name

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()