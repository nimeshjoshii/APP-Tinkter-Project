"""
Smart Exam Hall – Anti-Cheating Seat Allocator
Tkinter (frontend) + MySQL (backend)

Run setup.sql in MySQL Workbench first, then launch this app.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import csv
import mysql.connector

# ── Database configuration ──────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "Ni@040108", 
    "database": "exam_hall_db",
}


def run_query(query, params=(), fetch=False):
    """Open a connection, execute, commit or fetch, then always close."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(query, params)
    if fetch:
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    conn.commit()
    cur.close()
    conn.close()


# ── Colour palette for subject-coded seats ──────────────────
COLOUR_POOL = [
    "#AED6F1",  # light blue
    "#A9DFBF",  # light green
    "#F9E79F",  # light yellow
    "#F5B7B1",  # light red
    "#D7BDE2",  # light purple
    "#A3E4D7",  # aqua
    "#FDEBD0",  # peach
    "#D5F5E3",  # mint
    "#FADBD8",  # blush
    "#D6EAF8",  # sky
    "#E8DAEF",  # lavender
    "#FCF3CF",  # cream
]
EMPTY_COLOUR = "#D5D8DC"


class ExamHallApp:
    """Main application class – one Notebook with five tabs."""

    def __init__(self, root):
        self.root = root
        self.root.title("Smart Exam Hall – Anti-Cheating Seat Allocator")
        self.root.geometry("980x660")
        self.root.resizable(True, True)

        # Map subject_code → colour (assigned dynamically)
        self.subject_colours = {}

        # Notebook
        self.nb = ttk.Notebook(root)
        self.nb.pack(fill="both", expand=True, padx=6, pady=6)

        self._build_students_tab()
        self._build_halls_tab()
        self._build_allocate_tab()
        self._build_chart_tab()
        self._build_find_tab()

    # ================================================================
    # TAB 1 – Students
    # ================================================================
    def _build_students_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  Students  ")

        # ── form ──
        form = ttk.LabelFrame(tab, text="Student Details")
        form.pack(fill="x", padx=8, pady=(8, 2))

        labels = ("Reg No", "Name", "Branch", "Subject Code")
        self.stu_vars = {}
        for i, lbl in enumerate(labels):
            ttk.Label(form, text=lbl + ":").grid(
                row=0, column=i * 2, padx=5, pady=6, sticky="e")
            var = tk.StringVar()
            ttk.Entry(form, textvariable=var, width=18).grid(
                row=0, column=i * 2 + 1, padx=5, pady=6)
            self.stu_vars[lbl] = var

        # ── buttons ──
        bf = ttk.Frame(tab)
        bf.pack(fill="x", padx=8)
        for txt, cmd in [("Add", self._add_student),
                         ("Update", self._update_student),
                         ("Delete", self._delete_student),
                         ("Clear", self._clear_student_form)]:
            ttk.Button(bf, text=txt, command=cmd).pack(side="left", padx=4, pady=4)

        # ── search ──
        sf = ttk.Frame(tab)
        sf.pack(fill="x", padx=8)
        ttk.Label(sf, text="Search:").pack(side="left", padx=4)
        self.stu_search = tk.StringVar()
        ttk.Entry(sf, textvariable=self.stu_search, width=24).pack(side="left", padx=4)
        ttk.Button(sf, text="Go", command=self._search_students).pack(side="left", padx=4)
        ttk.Button(sf, text="Show All", command=self._load_students).pack(side="left", padx=4)

        # ── treeview ──
        tf = ttk.Frame(tab)
        tf.pack(fill="both", expand=True, padx=8, pady=4)
        cols = ("ID", "Reg No", "Name", "Branch", "Subject Code")
        self.stu_tree = ttk.Treeview(tf, columns=cols, show="headings", height=14)
        for c in cols:
            self.stu_tree.heading(c, text=c)
            self.stu_tree.column(c, width=120, anchor="center")
        self.stu_tree.column("Name", width=180)
        vsb = ttk.Scrollbar(tf, orient="vertical", command=self.stu_tree.yview)
        self.stu_tree.configure(yscrollcommand=vsb.set)
        self.stu_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.stu_tree.bind("<<TreeviewSelect>>", self._on_student_select)

        self._load_students()

    # ── student helpers ──────────────────────────────────────
    def _load_students(self):
        """Refresh the student treeview with all rows."""
        for i in self.stu_tree.get_children():
            self.stu_tree.delete(i)
        try:
            rows = run_query(
                "SELECT id, reg_no, name, branch, subject_code "
                "FROM students ORDER BY id", fetch=True)
            for r in rows:
                self.stu_tree.insert("", "end", values=r)
        except mysql.connector.Error as e:
            messagebox.showerror("DB Error", str(e))

    def _search_students(self):
        term = self.stu_search.get().strip()
        if not term:
            self._load_students()
            return
        for i in self.stu_tree.get_children():
            self.stu_tree.delete(i)
        try:
            like = f"%{term}%"
            rows = run_query(
                "SELECT id, reg_no, name, branch, subject_code FROM students "
                "WHERE reg_no LIKE %s OR name LIKE %s "
                "OR branch LIKE %s OR subject_code LIKE %s ORDER BY id",
                (like, like, like, like), fetch=True)
            for r in rows:
                self.stu_tree.insert("", "end", values=r)
        except mysql.connector.Error as e:
            messagebox.showerror("DB Error", str(e))

    def _add_student(self):
        reg  = self.stu_vars["Reg No"].get().strip()
        name = self.stu_vars["Name"].get().strip()
        br   = self.stu_vars["Branch"].get().strip()
        subj = self.stu_vars["Subject Code"].get().strip()
        if not all([reg, name, br, subj]):
            messagebox.showwarning("Validation", "All fields are required.")
            return
        try:
            run_query(
                "INSERT INTO students (reg_no, name, branch, subject_code) "
                "VALUES (%s, %s, %s, %s)", (reg, name, br, subj))
            self._load_students()
            self._clear_student_form()
        except mysql.connector.Error as e:
            messagebox.showerror("DB Error", str(e))

    def _update_student(self):
        sel = self.stu_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a student to update.")
            return
        sid  = self.stu_tree.item(sel[0], "values")[0]
        reg  = self.stu_vars["Reg No"].get().strip()
        name = self.stu_vars["Name"].get().strip()
        br   = self.stu_vars["Branch"].get().strip()
        subj = self.stu_vars["Subject Code"].get().strip()
        if not all([reg, name, br, subj]):
            messagebox.showwarning("Validation", "All fields are required.")
            return
        try:
            run_query(
                "UPDATE students SET reg_no=%s, name=%s, branch=%s, "
                "subject_code=%s WHERE id=%s",
                (reg, name, br, subj, sid))
            self._load_students()
            self._clear_student_form()
        except mysql.connector.Error as e:
            messagebox.showerror("DB Error", str(e))

    def _delete_student(self):
        sel = self.stu_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a student to delete.")
            return
        if not messagebox.askyesno("Confirm", "Delete this student?"):
            return
        sid = self.stu_tree.item(sel[0], "values")[0]
        try:
            run_query("DELETE FROM students WHERE id=%s", (sid,))
            self._load_students()
            self._clear_student_form()
        except mysql.connector.Error as e:
            messagebox.showerror("DB Error", str(e))

    def _on_student_select(self, _event=None):
        sel = self.stu_tree.selection()
        if not sel:
            return
        vals = self.stu_tree.item(sel[0], "values")
        for key, val in zip(("Reg No", "Name", "Branch", "Subject Code"), vals[1:]):
            self.stu_vars[key].set(val)

    def _clear_student_form(self):
        for v in self.stu_vars.values():
            v.set("")
        self.stu_tree.selection_remove(*self.stu_tree.selection())

    # ================================================================
    # TAB 2 – Halls
    # ================================================================
    def _build_halls_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  Halls  ")

        # ── form ──
        form = ttk.LabelFrame(tab, text="Hall Details")
        form.pack(fill="x", padx=8, pady=(8, 2))
        self.hall_vars = {}
        for i, (lbl, w) in enumerate([("Hall Name", 18), ("Rows", 6), ("Columns", 6)]):
            ttk.Label(form, text=lbl + ":").grid(
                row=0, column=i * 2, padx=5, pady=6, sticky="e")
            var = tk.StringVar()
            ttk.Entry(form, textvariable=var, width=w).grid(
                row=0, column=i * 2 + 1, padx=5, pady=6)
            self.hall_vars[lbl] = var

        bf = ttk.Frame(tab)
        bf.pack(fill="x", padx=8)
        ttk.Button(bf, text="Add", command=self._add_hall).pack(side="left", padx=4, pady=4)
        ttk.Button(bf, text="Delete", command=self._delete_hall).pack(side="left", padx=4, pady=4)
        ttk.Button(bf, text="Clear", command=self._clear_hall_form).pack(side="left", padx=4, pady=4)

        # ── treeview ──
        tf = ttk.Frame(tab)
        tf.pack(fill="both", expand=True, padx=8, pady=4)
        cols = ("ID", "Hall Name", "Rows", "Columns", "Capacity")
        self.hall_tree = ttk.Treeview(tf, columns=cols, show="headings", height=10)
        for c in cols:
            self.hall_tree.heading(c, text=c)
            self.hall_tree.column(c, width=120, anchor="center")
        vsb = ttk.Scrollbar(tf, orient="vertical", command=self.hall_tree.yview)
        self.hall_tree.configure(yscrollcommand=vsb.set)
        self.hall_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self._load_halls()

    def _load_halls(self):
        for i in self.hall_tree.get_children():
            self.hall_tree.delete(i)
        try:
            rows = run_query(
                "SELECT id, hall_name, total_rows, total_cols FROM halls ORDER BY id",
                fetch=True)
            for r in rows:
                self.hall_tree.insert("", "end", values=(*r, r[2] * r[3]))
        except mysql.connector.Error as e:
            messagebox.showerror("DB Error", str(e))

    def _add_hall(self):
        name = self.hall_vars["Hall Name"].get().strip()
        if not name:
            messagebox.showwarning("Validation", "Hall name is required.")
            return
        try:
            r = int(self.hall_vars["Rows"].get())
            c = int(self.hall_vars["Columns"].get())
            if r <= 0 or c <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation",
                                   "Rows and Columns must be positive integers.")
            return
        try:
            run_query(
                "INSERT INTO halls (hall_name, total_rows, total_cols) "
                "VALUES (%s, %s, %s)", (name, r, c))
            self._load_halls()
            self._clear_hall_form()
        except mysql.connector.Error as e:
            messagebox.showerror("DB Error", str(e))

    def _delete_hall(self):
        sel = self.hall_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a hall to delete.")
            return
        if not messagebox.askyesno("Confirm",
                                    "Delete this hall and its allocations?"):
            return
        hid = self.hall_tree.item(sel[0], "values")[0]
        try:
            run_query("DELETE FROM halls WHERE id=%s", (hid,))
            self._load_halls()
        except mysql.connector.Error as e:
            messagebox.showerror("DB Error", str(e))

    def _clear_hall_form(self):
        for v in self.hall_vars.values():
            v.set("")

    # ================================================================
    # TAB 3 – Allocate Seats
    # ================================================================
    def _build_allocate_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  Allocate Seats  ")

        bf = ttk.Frame(tab)
        bf.pack(pady=14)
        ttk.Button(bf, text="⚙  Generate Allocation",
                   command=self._generate_allocation).pack(side="left", padx=8)
        ttk.Button(bf, text="🗑  Clear Allocation",
                   command=self._clear_allocation).pack(side="left", padx=8)
        ttk.Button(bf, text="📄  Export to CSV",
                   command=self._export_csv).pack(side="left", padx=8)

        self.alloc_text = tk.Text(tab, height=20, width=96, state="disabled",
                                  font=("Consolas", 10))
        self.alloc_text.pack(padx=10, pady=6, fill="both", expand=True)

        self._refresh_alloc_summary()

    def _refresh_alloc_summary(self):
        """Show current allocation statistics."""
        self.alloc_text.configure(state="normal")
        self.alloc_text.delete("1.0", "end")
        try:
            total_stu = run_query(
                "SELECT COUNT(*) FROM students", fetch=True)[0][0]
            allocated = run_query(
                "SELECT COUNT(*) FROM allocations", fetch=True)[0][0]
            unseated = total_stu - allocated

            hall_usage = run_query(
                "SELECT h.hall_name, h.total_rows * h.total_cols AS cap, "
                "COUNT(a.id) AS filled "
                "FROM halls h LEFT JOIN allocations a ON h.id = a.hall_id "
                "GROUP BY h.id, h.hall_name, cap ORDER BY h.id", fetch=True)

            lines = [
                "╔══════════════════════════════════════════╗",
                "║       SEAT ALLOCATION SUMMARY            ║",
                "╚══════════════════════════════════════════╝",
                "",
                f"  Total students   : {total_stu}",
                f"  Allocated        : {allocated}",
                f"  Unseated         : {unseated}",
                "",
                "  Hall-wise usage:",
                "  " + "─" * 44,
                f"  {'Hall':<20s} {'Filled':>8s} {'Capacity':>10s}",
                "  " + "─" * 44,
            ]
            for hname, cap, filled in hall_usage:
                lines.append(f"  {hname:<20s} {filled:>8d} {cap:>10d}")
            lines.append("  " + "─" * 44)

            if allocated == 0:
                lines += ["",
                           "  No allocation yet.  Click  ⚙ Generate Allocation  to begin."]
            elif unseated > 0:
                lines += ["",
                           "  ⚠  Some students could not be seated.",
                           "     Add more halls or increase capacity and regenerate."]
            else:
                lines += ["",
                           "  ✅  All students have been seated successfully."]

            self.alloc_text.insert("1.0", "\n".join(lines))
        except mysql.connector.Error as e:
            self.alloc_text.insert("1.0", f"Database error: {e}")
        self.alloc_text.configure(state="disabled")

    # ── core anti-cheating algorithm ─────────────────────────
    def _generate_allocation(self):
        """
        Allocate students to seats so that no two neighbours (left, right,
        front, back) share the same subject_code (hard rule).  Also try to
        avoid the same branch in adjacent seats (soft rule – relaxed when
        impossible).
        """
        try:
            # If allocation already exists, ask to replace
            existing = run_query(
                "SELECT COUNT(*) FROM allocations", fetch=True)[0][0]
            if existing:
                if not messagebox.askyesno(
                        "Existing Allocation",
                        "An allocation already exists.\n"
                        "Clear it and generate a new one?"):
                    return
                run_query("DELETE FROM allocations")

            students = run_query(
                "SELECT id, reg_no, name, branch, subject_code "
                "FROM students ORDER BY id", fetch=True)
            halls = run_query(
                "SELECT id, hall_name, total_rows, total_cols "
                "FROM halls ORDER BY id", fetch=True)

            if not students:
                messagebox.showwarning("No Data", "No students in the database.")
                return
            if not halls:
                messagebox.showwarning("No Data", "No halls in the database.")
                return

            total_seats = sum(h[2] * h[3] for h in halls)
            if total_seats < len(students):
                shortage = len(students) - total_seats
                messagebox.showerror(
                    "Insufficient Seats",
                    f"Need {len(students)} seats but only {total_seats} "
                    f"available (shortage: {shortage}).\n"
                    "Add more halls or increase capacity.")
                return

            # Shuffle for randomness each run
            pool = list(students)
            random.shuffle(pool)

            # grid[hall_id][(row, col)] → (student_id, branch, subject_code)
            grid = {}
            placed = []           # (student_id, hall_id, row, col)

            for hall_id, _hname, rows, cols in halls:
                grid[hall_id] = {}
                for r in range(1, rows + 1):
                    for c in range(1, cols + 1):
                        if not pool:
                            break

                        # Collect already-placed neighbour info
                        nb_subj   = set()
                        nb_branch = set()
                        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                            nb = grid[hall_id].get((r + dr, c + dc))
                            if nb:
                                nb_subj.add(nb[2])
                                nb_branch.add(nb[1])

                        chosen_idx = None

                        # Pass 1 – no subject AND no branch conflict
                        for idx, stu in enumerate(pool):
                            if (stu[4] not in nb_subj and
                                    stu[3] not in nb_branch):
                                chosen_idx = idx
                                break

                        # Pass 2 – enforce subject only (relax branch)
                        if chosen_idx is None:
                            for idx, stu in enumerate(pool):
                                if stu[4] not in nb_subj:
                                    chosen_idx = idx
                                    break

                        # Pass 3 – last resort (should be very rare)
                        if chosen_idx is None:
                            chosen_idx = 0

                        chosen = pool.pop(chosen_idx)
                        grid[hall_id][(r, c)] = (
                            chosen[0], chosen[3], chosen[4])
                        placed.append((chosen[0], hall_id, r, c))

                    if not pool:
                        break

            # Persist allocations
            for sid, hid, r, c in placed:
                run_query(
                    "INSERT INTO allocations "
                    "(student_id, hall_id, row_no, col_no) "
                    "VALUES (%s, %s, %s, %s)", (sid, hid, r, c))

            messagebox.showinfo(
                "Done",
                f"Allocated {len(placed)} of {len(students)} students.")
            self._refresh_alloc_summary()
            # Also refresh chart dropdown in case halls changed
            self._refresh_hall_combo()

        except mysql.connector.Error as e:
            messagebox.showerror("DB Error", str(e))

    def _clear_allocation(self):
        if not messagebox.askyesno("Confirm",
                                    "Clear ALL seat allocations?"):
            return
        try:
            run_query("DELETE FROM allocations")
            self._refresh_alloc_summary()
            messagebox.showinfo("Cleared", "All allocations removed.")
        except mysql.connector.Error as e:
            messagebox.showerror("DB Error", str(e))

    # ── CSV export ───────────────────────────────────────────
    def _export_csv(self):
        try:
            rows = run_query(
                "SELECT s.reg_no, s.name, s.branch, s.subject_code, "
                "h.hall_name, a.row_no, a.col_no "
                "FROM allocations a "
                "JOIN students s ON a.student_id = s.id "
                "JOIN halls h    ON a.hall_id    = h.id "
                "ORDER BY h.hall_name, a.row_no, a.col_no", fetch=True)
            if not rows:
                messagebox.showinfo("Empty", "No allocation data to export.")
                return
            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Save Allocation CSV")
            if not path:
                return
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Reg No", "Name", "Branch", "Subject Code",
                            "Hall", "Row", "Column"])
                w.writerows(rows)
            messagebox.showinfo("Exported", f"Saved to:\n{path}")
        except (mysql.connector.Error, OSError) as e:
            messagebox.showerror("Error", str(e))

    # ================================================================
    # TAB 4 – Seating Chart
    # ================================================================
    def _build_chart_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  Seating Chart  ")

        # Hall selector
        top = ttk.Frame(tab)
        top.pack(fill="x", padx=8, pady=6)
        ttk.Label(top, text="Select Hall:").pack(side="left", padx=4)
        self.chart_hall_var = tk.StringVar()
        self.chart_combo = ttk.Combobox(
            top, textvariable=self.chart_hall_var,
            state="readonly", width=22)
        self.chart_combo.pack(side="left", padx=4)
        ttk.Button(top, text="Show Chart",
                   command=self._show_chart).pack(side="left", padx=8)

        # Legend
        self.legend_frame = ttk.LabelFrame(tab, text="Legend  (colour = subject)")
        self.legend_frame.pack(fill="x", padx=8)

        # Scrollable canvas for the grid
        cf = ttk.Frame(tab)
        cf.pack(fill="both", expand=True, padx=8, pady=4)
        self.chart_canvas = tk.Canvas(cf, bg="white")
        vsb = ttk.Scrollbar(cf, orient="vertical",
                            command=self.chart_canvas.yview)
        hsb = ttk.Scrollbar(cf, orient="horizontal",
                            command=self.chart_canvas.xview)
        self.chart_canvas.configure(yscrollcommand=vsb.set,
                                    xscrollcommand=hsb.set)
        hsb.pack(side="bottom", fill="x")
        vsb.pack(side="right", fill="y")
        self.chart_canvas.pack(side="left", fill="both", expand=True)

        # Inner frame placed on the canvas
        self.chart_inner = ttk.Frame(self.chart_canvas)
        self.chart_canvas.create_window((0, 0), window=self.chart_inner,
                                        anchor="nw")
        self.chart_inner.bind(
            "<Configure>",
            lambda _: self.chart_canvas.configure(
                scrollregion=self.chart_canvas.bbox("all")))

        self._refresh_hall_combo()

    def _refresh_hall_combo(self):
        try:
            halls = run_query(
                "SELECT hall_name FROM halls ORDER BY id", fetch=True)
            self.chart_combo["values"] = [h[0] for h in halls]
        except mysql.connector.Error:
            pass

    def _colour_for_subject(self, subj):
        """Return a consistent colour for the given subject code."""
        if subj not in self.subject_colours:
            idx = len(self.subject_colours) % len(COLOUR_POOL)
            self.subject_colours[subj] = COLOUR_POOL[idx]
        return self.subject_colours[subj]

    def _show_chart(self):
        self._refresh_hall_combo()
        hall_name = self.chart_hall_var.get()
        if not hall_name:
            messagebox.showwarning("Select Hall", "Choose a hall first.")
            return

        # Clear previous grid & legend
        for w in self.chart_inner.winfo_children():
            w.destroy()
        for w in self.legend_frame.winfo_children():
            w.destroy()

        try:
            hall = run_query(
                "SELECT id, total_rows, total_cols FROM halls "
                "WHERE hall_name = %s", (hall_name,), fetch=True)
            if not hall:
                return
            hall_id, rows, cols = hall[0]

            allocs = run_query(
                "SELECT a.row_no, a.col_no, s.reg_no, s.subject_code "
                "FROM allocations a "
                "JOIN students s ON a.student_id = s.id "
                "WHERE a.hall_id = %s", (hall_id,), fetch=True)
            seat_map = {(r, c): (reg, subj) for r, c, reg, subj in allocs}

            # Column headers
            tk.Label(self.chart_inner, text="", width=7).grid(
                row=0, column=0)
            for c in range(1, cols + 1):
                tk.Label(self.chart_inner, text=f"Col {c}",
                         font=("Arial", 8, "bold"), width=14).grid(
                    row=0, column=c, padx=1, pady=1)

            subjects_seen = set()

            for r in range(1, rows + 1):
                tk.Label(self.chart_inner, text=f"Row {r}",
                         font=("Arial", 8, "bold"), width=7).grid(
                    row=r, column=0, padx=1, pady=1)
                for c in range(1, cols + 1):
                    if (r, c) in seat_map:
                        reg, subj = seat_map[(r, c)]
                        bg = self._colour_for_subject(subj)
                        text = f"{reg}\n{subj}"
                        subjects_seen.add(subj)
                    else:
                        bg = EMPTY_COLOUR
                        text = "—"

                    tk.Label(
                        self.chart_inner, text=text, bg=bg,
                        relief="ridge", width=14, height=3,
                        font=("Consolas", 8), anchor="center"
                    ).grid(row=r, column=c, padx=1, pady=1)

            # Build legend
            for subj in sorted(subjects_seen):
                frm = tk.Frame(self.legend_frame)
                frm.pack(side="left", padx=8, pady=4)
                tk.Label(frm, text="  ", bg=self._colour_for_subject(subj),
                         relief="solid", width=3).pack(side="left")
                tk.Label(frm, text=f" {subj}").pack(side="left")

            frm = tk.Frame(self.legend_frame)
            frm.pack(side="left", padx=8, pady=4)
            tk.Label(frm, text="  ", bg=EMPTY_COLOUR,
                     relief="solid", width=3).pack(side="left")
            tk.Label(frm, text=" Empty").pack(side="left")

        except mysql.connector.Error as e:
            messagebox.showerror("DB Error", str(e))

    # ================================================================
    # TAB 5 – Find My Seat
    # ================================================================
    def _build_find_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  Find My Seat  ")

        frm = ttk.Frame(tab)
        frm.pack(pady=50)
        ttk.Label(frm, text="Enter Registration No:",
                  font=("Arial", 13)).pack(pady=8)
        self.find_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.find_var, width=22,
                  font=("Arial", 13)).pack(pady=8)
        ttk.Button(frm, text="🔍  Find Seat",
                   command=self._find_seat).pack(pady=12)

        self.find_result = tk.Label(
            tab, text="", font=("Consolas", 14), justify="center")
        self.find_result.pack(pady=16)

    def _find_seat(self):
        reg = self.find_var.get().strip()
        if not reg:
            messagebox.showwarning("Input Required",
                                   "Please enter a registration number.")
            return
        try:
            rows = run_query(
                "SELECT h.hall_name, a.row_no, a.col_no, "
                "s.name, s.subject_code "
                "FROM allocations a "
                "JOIN students s ON a.student_id = s.id "
                "JOIN halls    h ON a.hall_id    = h.id "
                "WHERE s.reg_no = %s", (reg,), fetch=True)
            if rows:
                hall, r, c, name, subj = rows[0]
                self.find_result.config(
                    text=(f"🎓  {name}  ({reg})\n\n"
                          f"Subject : {subj}\n"
                          f"Hall    : {hall}\n"
                          f"Row     : {r}\n"
                          f"Column  : {c}"),
                    fg="#1A5276")
            else:
                self.find_result.config(
                    text=(f"No seat found for '{reg}'.\n"
                          "Student may not exist or is not allocated yet."),
                    fg="#922B21")
        except mysql.connector.Error as e:
            messagebox.showerror("DB Error", str(e))


# ── Entry point ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    ExamHallApp(root)
    root.mainloop()
