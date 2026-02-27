import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Professional Plotter", layout="wide")

st.title("Experimentalist: Plotter")

# =============================
# Two Column Layout
# =============================
left_col, right_col = st.columns([1.2, 1])

# =============================
# LEFT SIDE — CONTROLS
# =============================
with left_col:

    st.header("Controls")

    # -------------------------
    # File Upload
    # -------------------------
    uploaded_files = st.file_uploader(
        "Upload CSV or XLSX files",
        type=["csv", "xlsx"],
        accept_multiple_files=True
    )

    skiprows = st.number_input("Rows to skip", 0, 1000, 0)

    data_dict = {}

    if uploaded_files:
        for file in uploaded_files:
            try:
                if file.name.endswith(".csv"):
                    df = pd.read_csv(file, skiprows=skiprows)
                else:
                    df = pd.read_excel(file, skiprows=skiprows)
                data_dict[file.name] = df
            except Exception as e:
                st.error(f"Error loading {file.name}: {e}")

    if not data_dict:
        st.stop()


    # =============================
    # Initialize Colour Groups
    # =============================

    if "color_groups" not in st.session_state:

        default_colors = [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#8c564b",
            "#e377c2",
            "#7f7f7f",
            "#bcbd22",
            "#17becf",
        ]

        st.session_state.color_groups = []

        for i, filename in enumerate(data_dict.keys()):

            color = default_colors[i % len(default_colors)]

            st.session_state.color_groups.append({
                "name": filename,          # group named after file
                "color": color,
                "files": [filename]        # one file per group
            })

    # =============================
    # Sync New / Deleted Files
    # =============================

    all_files = list(data_dict.keys())

    # Flatten existing assignments
    assigned_files = [
        f
        for group in st.session_state.color_groups
        for f in group["files"]
    ]

    # Add new files as new individual groups
    default_colors = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ]

    for i, f in enumerate(all_files):
        if f not in assigned_files:
            st.session_state.color_groups.append({
                "name": f,
                "color": default_colors[len(st.session_state.color_groups) % len(default_colors)],
                "files": [f]
            })

    # Remove deleted files
    for group in st.session_state.color_groups:
        group["files"] = [f for f in group["files"] if f in all_files]

    # =============================
    # Persistent File State
    # =============================

    if "file_order" not in st.session_state:
        st.session_state.file_order = list(data_dict.keys())

    if "file_meta" not in st.session_state:
        st.session_state.file_meta = {
            name: {
                "group": "Blue",
            }
            for name in data_dict.keys()
        }

    # Sync new/deleted files
    for f in data_dict:
        if f not in st.session_state.file_order:
            st.session_state.file_order.append(f)
            st.session_state.file_meta[f] = {"group": "Blue"}

    st.session_state.file_order = [
        f for f in st.session_state.file_order if f in data_dict
    ]

    # -------------------------
    # Global Plot Settings
    # -------------------------
    st.subheader("Global Plot Settings")

    fig_width = st.number_input("Figure Width", 2.0, 20.0, 6.0)
    fig_height = st.number_input("Figure Height", 2.0, 15.0, 4.0)
    dpi = st.number_input("DPI", 50, 600, 100)

    plot_title = st.text_input("Title", "My Plot")
    x_label = st.text_input("X Label", "X")
    y_label = st.text_input("Y Label", "Y")
    legend_loc = st.selectbox(
        "Legend Location",
        ["best", "upper right", "upper left", "lower left", "lower right", "right", "center left", "center right", "lower center", "upper center", "center"]
    )

    # -------------------------
    # Global File Defaults
    # -------------------------
    st.subheader("Global File Defaults")

    first_filename = list(data_dict.keys())[0]
    first_df = data_dict[first_filename]
    first_columns = first_df.columns.tolist()

    st.caption(f"Columns from: {first_filename}")

    global_x = st.selectbox("Global X Column", first_columns)
    global_y = st.selectbox("Global Y Column", first_columns)

    global_color = st.color_picker("Global Color", "#1f77b4")
    global_linestyle = st.selectbox(
        "Global Line Style",
        ["-", "--", "-.", ":", "None"]
    )
    global_linewidth = st.slider("Global Line Width", 0.5, 10.0, 1.5)
    global_alpha = st.slider("Global Alpha", 0.0, 1.0, 1.0)

    if global_linestyle == "None":
        global_linestyle = None

    

    # =============================
    # File Order Management
    # =============================

    if "file_order" not in st.session_state:
        st.session_state.file_order = list(data_dict.keys())

    # Remove deleted files
    st.session_state.file_order = [
        f for f in st.session_state.file_order if f in data_dict
    ]

    # Add new files
    for f in data_dict.keys():
        if f not in st.session_state.file_order:
            st.session_state.file_order.append(f)

    st.subheader("Colour Groups")

    if st.button("➕ Add Colour Group"):
        new_index = len(st.session_state.color_groups) + 1
        st.session_state.color_groups.append({
            "name": f"Group {new_index}",
            "color": "#ff7f0e",
            "files": []
        })
        st.rerun()

    # =============================
    # File Manager
    # =============================

    file_settings = {}

    for g_index, group in enumerate(st.session_state.color_groups):

        st.markdown("---")
        header_cols = st.columns([3, 1])

        # Editable group name
        group["name"] = header_cols[0].text_input(
            "Group Name",
            group["name"],
            key=f"group_name_{g_index}"
        )

        # Group colour picker
        group["color"] = header_cols[1].color_picker(
            "Colour",
            group["color"],
            key=f"group_color_{g_index}"
        )

        st.markdown(f"### {group['name']}")

        for filename in group["files"]:

            row = st.columns([1, 4])

            # Move to another group
            target_groups = [
                g["name"] for g in st.session_state.color_groups
            ]

            selected_target = row[0].selectbox(
                "",
                target_groups,
                index=g_index,
                key=f"move_{filename}",
                label_visibility="collapsed"
            )

            if selected_target != group["name"]:

                # Remove from current group
                group["files"].remove(filename)

                # Add to target group (append at bottom)
                for g in st.session_state.color_groups:
                    if g["name"] == selected_target:
                        g["files"].append(filename)

                st.rerun()

            # File expander
            with row[1].expander(filename):

                df = data_dict[filename]
                columns = df.columns.tolist()

                show = st.checkbox("Show", True, key=f"show_{filename}")
                legend = st.text_input("Legend", filename, key=f"leg_{filename}")

                override_x = st.selectbox(
                    "Override X",
                    ["Use Global"] + columns,
                    key=f"x_{filename}"
                )

                override_y = st.selectbox(
                    "Override Y",
                    ["Use Global"] + columns,
                    key=f"y_{filename}"
                )

                use_override_color = st.checkbox(
                    "Use Override Colour",
                    False,
                    key=f"use_override_color_{filename}"
                )

                override_color = st.color_picker(
                    "Override Colour",
                    group["color"],
                    key=f"c_{filename}"
                )

                override_linestyle = st.selectbox(
                    "Override Line Style",
                    ["Use Global", "-", "--", "-.", ":", "None"],
                    key=f"ls_{filename}"
                )

                # Line Width
                use_override_linewidth = st.checkbox(
                    "Override Line Width",
                    False,
                    key=f"lw_mode_{filename}"
                )

                override_linewidth = st.slider(
                    "Line Width Value",
                    0.5, 10.0, 1.5,
                    key=f"lw_val_{filename}"
                )


                # Alpha
                use_override_alpha = st.checkbox(
                    "Override Alpha",
                    False,
                    key=f"use_override_alpha_{filename}"
                )

                override_alpha = st.slider(
                    "Alpha Value",
                    0.0, 1.0, 1.0,
                    key=f"alpha_val_{filename}"
                )


                # Marker
                override_marker = st.selectbox(
                    "Marker",
                    ["Use Global", "None", "o", "s", "^", "v", "D", "x", "+"],
                    key=f"marker_{filename}"
                )

                # Marker Size
                use_override_markersize = st.checkbox(
                    "Override Marker Size",
                    False,
                    key=f"use_override_ms_{filename}"
                )

                override_markersize = st.slider(
                    "Marker Size Value",
                    1, 20, 6,
                    key=f"ms_val_{filename}"
                )


                # Z Order
                use_override_zorder = st.checkbox(
                    "Override Z Order",
                    False,
                    key=f"use_override_zorder_{filename}"
                )

                override_zorder = st.number_input(
                    "Z Order Value",
                    value=1,
                    key=f"z_val_{filename}"
                )

                file_settings[filename] = {
                    "show": show,
                    "legend": legend,
                    "override_x": override_x,
                    "override_y": override_y,
                    "group_color": group["color"],
                    "use_override_color": use_override_color,
                    "override_color": override_color,
                    "use_override_linestyle": override_linestyle != "Use Global",
                    "linestyle": override_linestyle,
                    "use_override_linewidth": use_override_linewidth,
                    "linewidth": override_linewidth,
                    "use_override_alpha": use_override_alpha,
                    "alpha": override_alpha,
                    "use_override_marker": override_marker != "Use Global",
                    "marker": override_marker,
                    "use_override_markersize": use_override_markersize,
                    "markersize": override_markersize,
                    "use_override_zorder": use_override_zorder,
                    "zorder": override_zorder,
                }
                    
# =============================
# RIGHT SIDE — PLOT
# =============================
with right_col:

    st.header("Plot")

    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)

    plotted = False

    for group in st.session_state.color_groups:

        for filename in group["files"]:

            if filename not in file_settings:
                continue

            s = file_settings[filename]

            if not s["show"]:
                continue

            df = data_dict[filename]
            columns = df.columns.tolist()

            x_col = global_x if s["override_x"] == "Use Global" else s["override_x"]
            y_col = global_y if s["override_y"] == "Use Global" else s["override_y"]

            if x_col not in columns or y_col not in columns:
                continue

            # -----------------------------
            # Resolve Style Precedence
            # -----------------------------

            # Colour
            if s["use_override_color"]:
                final_color = s["override_color"]
            else:
                final_color = s["group_color"]

            # Linestyle
            if s["linestyle"] == "Use Global":
                linestyle = global_linestyle
            elif s["linestyle"] == "None":
                linestyle = None
            else:
                linestyle = s["linestyle"]

            # Linewidth
            linewidth = s["linewidth"] if s["use_override_linewidth"] else global_linewidth

            # Alpha
            alpha = s["alpha"] if s["use_override_alpha"] else global_alpha

            # Marker
            if s["marker"] == "Use Global":
                marker = None
            elif s["marker"] == "None":
                marker = None
            else:
                marker = s["marker"]

            # Marker Size
            markersize = s["markersize"] if s["use_override_markersize"] else None

            # Z Order
            zorder = s["zorder"] if s["use_override_zorder"] else None

            ax.plot(
            df[x_col],
            df[y_col],
            label=s["legend"],
            color=final_color,
            linestyle=linestyle,
            linewidth=linewidth,
            alpha=alpha,
            marker=marker,
            markersize=markersize,
            zorder=zorder,
        )

        plotted = True

    if plotted:
        ax.set_title(plot_title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.legend(loc=legend_loc)
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("No valid datasets selected.")