"""
Smart Attendance System - Main GUI Application
Provides a user-friendly interface for attendance management.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import sys
import os
import shutil
import mysql.connector
from datetime import date, datetime
from typing import Optional, Tuple

import config
from logging_setup import get_logger

logger = get_logger(__name__)

# ══════════════════════════════════════════════════════════════
# Import color palette from config
# ══════════════════════════════════════════════════════════════
BG          = config.BG
BG2         = config.BG2
BG3         = config.BG3
BORDER      = config.BORDER
CYAN        = config.CYAN
CYAN_DIM    = config.CYAN_DIM
GREEN       = config.GREEN
GREEN_DIM   = config.GREEN_DIM
AMBER       = config.AMBER
RED         = config.RED
PURPLE      = config.PURPLE
TEXT        = config.TEXT
TEXT2       = config.TEXT2
TEXT3       = config.TEXT3
WHITE       = config.WHITE

FONT_TITLE  = ("Courier New", 20, "bold")
FONT_HEAD   = ("Courier New", 11, "bold")
FONT_BODY   = ("Courier New", 10)
FONT_SMALL  = ("Courier New", 8)
FONT_NUM    = ("Courier New", 28, "bold")

def get_conn():
    """Get a database connection."""
    try:
        return mysql.connector.connect(**config.DB_CONFIG)
    except mysql.connector.Error as e:
        logger.error(f"Database connection error: {e}")
        raise


# ══════════════════════════════════════════════════════════════
class AttendanceApp:
    """Main GUI application for Smart Attendance System."""
    
    def __init__(self, root: tk.Tk) -> None:
        """Initialize the application."""
        self.root = root
        self.root.title("SMART ATTENDANCE SYSTEM  v2.0")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self._active_process = None
        self._blink_state = True
        self._build_ui()
        self._refresh_stats()
        self._tick_clock()
        self._blink()

    # ══════════════════════════════════════════════════════════
    #  CLOCK + BLINK
    # ══════════════════════════════════════════════════════════
    def _tick_clock(self) -> None:
        """Update the clock display."""
        try:
            now = datetime.now()
            self.clock_lbl.configure(text=now.strftime("%H:%M:%S"))
        except Exception as e:
            logger.error(f"Error updating clock: {e}")
        self.root.after(config.CLOCK_UPDATE_INTERVAL, self._tick_clock)

    def _blink(self) -> None:
        """Blink the status indicator dot."""
        try:
            self._blink_state = not self._blink_state
            col = CYAN if self._blink_state else BG2
            self.blink_dot.configure(fg=col)
        except Exception as e:
            logger.error(f"Error updating blink: {e}")
        self.root.after(config.BLINK_FREQUENCY, self._blink)

    # ══════════════════════════════════════════════════════════
    #  MAIN UI
    # ══════════════════════════════════════════════════════════
    def _build_ui(self):
        self._build_header()
        self._build_body()

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=BG2, pady=0)
        hdr.pack(fill="x")

        # Top strip
        strip = tk.Frame(hdr, bg=BG2, padx=20, pady=12)
        strip.pack(fill="x")

        # Left: logo
        logo_f = tk.Frame(strip, bg=BG2)
        logo_f.pack(side="left")

        self.blink_dot = tk.Label(logo_f, text="◉", font=("Courier New", 20, "bold"),
                                   bg=BG2, fg=CYAN)
        self.blink_dot.pack(side="left", padx=(0, 8))

        tk.Label(logo_f, text="SMART", font=("Courier New", 18, "bold"),
                 bg=BG2, fg=WHITE).pack(side="left")
        tk.Label(logo_f, text="ATTENDANCE", font=("Courier New", 18, "bold"),
                 bg=BG2, fg=CYAN).pack(side="left", padx=(6, 0))

        tk.Label(logo_f, text="  SYS v2.0", font=("Courier New", 9),
                 bg=BG2, fg=TEXT2).pack(side="left", padx=(4, 0), anchor="s")

        # Right: clock + date + status
        right_f = tk.Frame(strip, bg=BG2)
        right_f.pack(side="right")

        self.status_lbl = tk.Label(right_f, text="● STANDBY",
                                    font=("Courier New", 9, "bold"),
                                    bg=BG2, fg=TEXT2)
        self.status_lbl.pack(side="right", padx=(12, 0))

        tk.Label(right_f, text=date.today().strftime("%d %b %Y").upper(),
                 font=FONT_SMALL, bg=BG2, fg=TEXT2).pack(side="right", padx=12)

        self.clock_lbl = tk.Label(right_f, text="00:00:00",
                                   font=("Courier New", 14, "bold"),
                                   bg=BG2, fg=CYAN)
        self.clock_lbl.pack(side="right")

        # Accent line with gradient effect using segments
        line_f = tk.Frame(hdr, bg=BG, height=1)
        line_f.pack(fill="x")
        tk.Frame(hdr, bg=CYAN, height=2).pack(fill="x")
        tk.Frame(hdr, bg=BG, height=1).pack(fill="x")

    def _build_body(self):
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=14)

        # Left sidebar
        sidebar = tk.Frame(body, bg=BG, width=260)
        sidebar.pack(side="left", fill="y", padx=(0, 12))
        sidebar.pack_propagate(False)

        # Center panel
        center = tk.Frame(body, bg=BG)
        center.pack(side="left", fill="both", expand=True)

        self._build_sidebar(sidebar)
        self._build_center(center)

    # ══════════════════════════════════════════════════════════
    #  SIDEBAR
    # ══════════════════════════════════════════════════════════
    def _build_sidebar(self, parent):
        # ── Stat cards ─────────────────────────────────────
        self.stat_students = self._stat_card(parent, "0",  "ENROLLED",     CYAN,      "👥")
        self.stat_today    = self._stat_card(parent, "0",  "PRESENT TODAY",GREEN,     "✓")
        self.stat_total    = self._stat_card(parent, "0",  "TOTAL RECORDS",AMBER,     "#")

        # Divider
        self._divider(parent)

        # ── Action buttons ──────────────────────────────────
        self._section_label(parent, "OPERATIONS")

        actions = [
            ("REGISTER STUDENT",  CYAN,   self.open_register,   "[ + ]"),
            ("MANAGE STUDENTS",   PURPLE, self.open_manage,     "[ ≡ ]"),
            ("START ATTENDANCE",  GREEN,  self.start_attendance,"[ ▶ ]"),
            ("UPDATE FACE MODEL", AMBER,  self.run_encoding,    "[ ⟳ ]"),
            ("SETUP DATABASE",    "#4f6ef7", self.run_db_setup, "[ ⊞ ]"),
            ("EXPORT CSV REPORT", "#a855f7", self.export_report,"[ ↓ ]"),
        ]

        for text, color, cmd, tag in actions:
            self._action_btn(parent, text, color, cmd, tag)

        self._divider(parent)

        # Refresh
        tk.Button(parent, text="[ ⟳ ]  REFRESH STATS",
                  font=FONT_SMALL, bg=BG3, fg=TEXT2,
                  bd=0, pady=7, cursor="hand2",
                  activebackground=BORDER, activeforeground=TEXT,
                  command=self._refresh_stats).pack(fill="x", pady=(2, 0))

    def _stat_card(self, parent, value, label, color, icon):
        card = tk.Frame(parent, bg=BG2, padx=0, pady=0)
        card.pack(fill="x", pady=3)

        # Left color bar
        tk.Frame(card, bg=color, width=3).pack(side="left", fill="y")

        inner = tk.Frame(card, bg=BG2, padx=12, pady=10)
        inner.pack(side="left", fill="x", expand=True)

        top_row = tk.Frame(inner, bg=BG2)
        top_row.pack(fill="x")

        lbl = tk.Label(top_row, text=value, font=FONT_NUM,
                       bg=BG2, fg=color)
        lbl.pack(side="left")

        tk.Label(top_row, text=icon, font=("Courier New", 18),
                 bg=BG2, fg=color).pack(side="right", padx=4)

        tk.Label(inner, text=label, font=FONT_SMALL,
                 bg=BG2, fg=TEXT2).pack(anchor="w")

        return lbl

    def _action_btn(self, parent, text, color, cmd, tag=""):
        f = tk.Frame(parent, bg=BG, pady=2)
        f.pack(fill="x")

        btn = tk.Button(f, text=f"{tag}  {text}",
                        font=("Courier New", 9, "bold"),
                        bg=BG3, fg=TEXT3,
                        bd=0, padx=12, pady=9,
                        cursor="hand2", anchor="w",
                        activebackground=BG2,
                        activeforeground=color,
                        command=cmd)
        btn.pack(fill="x")

        # Left accent on hover
        accent = tk.Frame(f, bg=BG3, width=3)
        accent.place(x=0, y=0, relheight=1)

        def on_enter(e):
            btn.configure(bg=BG2, fg=color)
            accent.configure(bg=color)

        def on_leave(e):
            btn.configure(bg=BG3, fg=TEXT3)
            accent.configure(bg=BG3)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def _section_label(self, parent, text):
        f = tk.Frame(parent, bg=BG, pady=4)
        f.pack(fill="x")
        tk.Label(f, text=f"── {text} ──",
                 font=("Courier New", 7, "bold"),
                 bg=BG, fg=TEXT2).pack(anchor="w")

    def _divider(self, parent):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=6)

    # ══════════════════════════════════════════════════════════
    #  CENTER PANEL
    # ══════════════════════════════════════════════════════════
    def _build_center(self, parent):
        # Top: log panel
        log_frame = tk.Frame(parent, bg=BG2)
        log_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Log header
        lhdr = tk.Frame(log_frame, bg=BG3, padx=14, pady=7)
        lhdr.pack(fill="x")

        tk.Label(lhdr, text="── SYSTEM LOG ──",
                 font=("Courier New", 8, "bold"),
                 bg=BG3, fg=TEXT2).pack(side="left")

        tk.Button(lhdr, text="CLEAR",
                  font=("Courier New", 7, "bold"),
                  bg=BG3, fg=TEXT2, bd=0, padx=8, pady=2,
                  cursor="hand2",
                  activebackground=BORDER, activeforeground=RED,
                  command=self._clear_log).pack(side="right")

        tk.Label(lhdr, text="LIVE OUTPUT",
                 font=("Courier New", 7),
                 bg=BG3, fg=TEXT2).pack(side="right", padx=10)

        # Log text box
        log_inner = tk.Frame(log_frame, bg=BG2, padx=2, pady=2)
        log_inner.pack(fill="both", expand=True)

        self.log_box = tk.Text(log_inner,
                                bg="#05080f", fg="#00ff9d",
                                font=("Courier New", 9),
                                bd=0, padx=14, pady=10,
                                insertbackground=CYAN,
                                wrap="word", state="disabled",
                                selectbackground=BORDER,
                                selectforeground=WHITE)
        sb = tk.Scrollbar(log_inner, bg=BG3, troughcolor=BG,
                          activebackground=CYAN, bd=0, width=8)
        sb.pack(side="right", fill="y")
        self.log_box.configure(yscrollcommand=sb.set)
        sb.configure(command=self.log_box.yview)
        self.log_box.pack(fill="both", expand=True)

        # Bottom: attendance table
        tbl_frame = tk.Frame(parent, bg=BG2)
        tbl_frame.pack(fill="x")

        thdr = tk.Frame(tbl_frame, bg=BG3, padx=14, pady=7)
        thdr.pack(fill="x")
        tk.Label(thdr, text="── TODAY'S ATTENDANCE ──",
                 font=("Courier New", 8, "bold"),
                 bg=BG3, fg=TEXT2).pack(side="left")

        self.today_count = tk.Label(thdr, text="0 PRESENT",
                                     font=("Courier New", 8, "bold"),
                                     bg=BG3, fg=GREEN)
        self.today_count.pack(side="right")

        # Table
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("T.Treeview",
                        background=BG2, foreground=TEXT,
                        fieldbackground=BG2,
                        font=("Courier New", 9),
                        rowheight=26, borderwidth=0)
        style.configure("T.Treeview.Heading",
                        background=BG3, foreground=CYAN,
                        font=("Courier New", 8, "bold"),
                        borderwidth=0, relief="flat")
        style.map("T.Treeview",
                  background=[("selected", "#1e3a4a")],
                  foreground=[("selected", CYAN)])

        cols = ("Roll No", "Name", "Department", "Time", "Status")
        self.table = ttk.Treeview(tbl_frame, columns=cols,
                                   show="headings",
                                   style="T.Treeview", height=7)
        for col, w, anchor in zip(cols,
                                   [90, 180, 130, 90, 80],
                                   ["center","w","w","center","center"]):
            self.table.heading(col, text=col.upper())
            self.table.column(col, width=w, anchor=anchor)

        self.table.pack(fill="x", padx=2, pady=(1, 2))
        self._refresh_table()

    # ══════════════════════════════════════════════════════════
    #  LOGGING
    # ══════════════════════════════════════════════════════════
    def _log(self, msg: str, level: str = "INFO") -> None:
        """
        Log a message to both GUI and file.
        
        Args:
            msg: Message to log
            level: Log level (INFO, OK, ERR, SYS)
        """
        def _do():
            self.log_box.configure(state="normal")
            ts = datetime.now().strftime("%H:%M:%S")
            colors = {"INFO": TEXT3, "OK": GREEN, "ERR": RED, "SYS": CYAN}
            tag = level
            self.log_box.tag_configure(tag, foreground=colors.get(level, TEXT3))
            self.log_box.insert("end", f"[{ts}]  {msg}\n", tag)
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        
        # Also log to file (map GUI levels to proper logging methods)
        if level.upper() == "OK":
            logger.info(msg)
        elif level.upper() == "ERR":
            logger.error(msg)
        elif level.upper() == "SYS":
            logger.info(msg)
        else:
            logger.info(msg)
        
        self.root.after(0, _do)

    def _clear_log(self) -> None:
        """Clear the log display."""
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    # ══════════════════════════════════════════════════════════
    #  STATS
    # ══════════════════════════════════════════════════════════
    def _refresh_stats(self) -> None:
        """Refresh statistics from database."""
        try:
            conn = get_conn()
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM students")
            n_students = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM attendance WHERE date=%s", (date.today(),))
            n_today = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM attendance")
            n_total = c.fetchone()[0]
            conn.close()

            self.stat_students.configure(text=str(n_students))
            self.stat_today.configure(text=str(n_today))
            self.stat_total.configure(text=str(n_total))
            self.today_count.configure(text=f"{n_today} PRESENT")
            self._refresh_table()
        except mysql.connector.Error as e:
            logger.error(f"Database error refreshing stats: {e}")
        except Exception as e:
            logger.error(f"Error refreshing stats: {e}")

    def _refresh_table(self) -> None:
        """Refresh the attendance table."""
        try:
            for i in self.table.get_children():
                self.table.delete(i)
            conn = get_conn()
            c = conn.cursor()
            c.execute("""SELECT s.roll_number,s.name,s.department,a.time,a.status
                         FROM attendance a
                         JOIN students s ON a.student_id=s.student_id
                         WHERE a.date=%s ORDER BY a.time""", (date.today(),))
            for i, row in enumerate(c.fetchall()):
                tag = "even" if i % 2 == 0 else "odd"
                self.table.insert("", "end",
                                  values=(row[0],row[1],row[2],str(row[3])[:8],row[4]),
                                  tags=(tag,))
            self.table.tag_configure("even", background=BG2)
            self.table.tag_configure("odd",  background=BG3)
            conn.close()
        except mysql.connector.Error as e:
            logger.error(f"Database error refreshing table: {e}")
        except Exception as e:
            logger.error(f"Error refreshing table: {e}")

    # ══════════════════════════════════════════════════════════
    #  STATUS DOT
    # ══════════════════════════════════════════════════════════
    def _set_status(self, text: str, color: str = TEXT2) -> None:
        """Update the status indicator."""
        try:
            self.status_lbl.configure(text=f"● {text}", fg=color)
        except Exception as e:
            logger.error(f"Error updating status: {e}")

    # ══════════════════════════════════════════════════════════
    #  SCRIPT RUNNER
    # ══════════════════════════════════════════════════════════
    def _run_script(self, script: str, label: str, color: str = GREEN) -> None:
        """
        Run a Python script in a background thread.
        
        Args:
            script: Script filename to run
            label: Display label for the operation
            color: Color to use for status indicator
        """
        def run():
            self._set_status(label.upper(), color)
            self._log(f"Starting {label}...", "SYS")
            try:
                proc = subprocess.Popen(
                    [sys.executable, script],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1
                )
                self._active_process = proc
                for line in proc.stdout:
                    stripped = line.strip()
                    if stripped:
                        level = "OK" if "✅" in stripped else "ERR" if "❌" in stripped else "INFO"
                        self._log(stripped, level)
                proc.wait()
                logger.info(f"{label} finished (exit code: {proc.returncode})")
                self._log(f"{label} finished.", "SYS")
            except FileNotFoundError:
                msg = f"{script} not found."
                logger.error(msg)
                self._log(f"❌ {msg}", "ERR")
            except Exception as e:
                msg = f"Error running {label}: {e}"
                logger.error(msg)
                self._log(f"❌ {msg}", "ERR")
            finally:
                self._set_status("STANDBY")
                self._refresh_stats()
        threading.Thread(target=run, daemon=True).start()

    def run_db_setup(self) -> None:
        """Run database setup script."""
        self._run_script("database_setup.py", "Database Setup", CYAN)

    def run_encoding(self) -> None:
        """Run face encoding script."""
        self._run_script("face_encoding.py",  "Face Encoding",  AMBER)

    def export_report(self) -> None:
        """Export attendance report to CSV."""
        self._log("Exporting attendance report...", "SYS")
        def run():
            try:
                import view_attendance
                f = view_attendance.export_to_csv()
                if f:
                    self._log(f"✅ Report saved: {f}", "OK")
                    messagebox.showinfo("Export Complete", f"Saved to:\n{f}")
                else:
                    self._log("❌ Export failed.", "ERR")
            except Exception as e:
                logger.error(f"Error exporting report: {e}")
                self._log(f"❌ Export failed: {e}", "ERR")
        threading.Thread(target=run, daemon=True).start()

    def start_attendance(self) -> None:
        """Start the attendance marking session."""
        if not os.path.exists(config.ENCODINGS_FILE):
            messagebox.showwarning("Model Missing",
                f"{config.ENCODINGS_FILE} not found!\nRun 'UPDATE FACE MODEL' first.")
            return
        self._log("▶ Launching attendance session...", "SYS")
        self._set_status("ATTENDING", GREEN)
        def run():
            try:
                subprocess.run([sys.executable, "auto_attendance.py"])
                logger.info("Attendance session ended")
            except Exception as e:
                logger.error(f"Error during attendance session: {e}")
                self._log(f"❌ Error: {e}", "ERR")
            finally:
                self._set_status("STANDBY")
                self._log("■ Attendance session ended.", "SYS")
                self._refresh_stats()
        threading.Thread(target=run, daemon=True).start()

    # ══════════════════════════════════════════════════════════
    #  POPUP HELPER
    # ══════════════════════════════════════════════════════════
    def _make_popup(self, title, w, h):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry(f"{w}x{h}")
        win.configure(bg=BG)
        win.grab_set()
        tk.Frame(win, bg=CYAN, height=2).pack(fill="x")
        return win

    def _popup_title(self, win, text, sub=""):
        tk.Label(win, text=text, font=("Courier New", 13, "bold"),
                 bg=BG, fg=CYAN).pack(pady=(18, 2))
        if sub:
            tk.Label(win, text=sub, font=FONT_SMALL,
                     bg=BG, fg=TEXT2).pack()

    def _field(self, parent, label, placeholder_or_value="", readonly=False):
        f = tk.Frame(parent, bg=BG); f.pack(fill="x", padx=28, pady=5)
        tk.Label(f, text=label.upper(), font=("Courier New", 7, "bold"),
                 bg=BG, fg=TEXT2).pack(anchor="w")

        e = tk.Entry(f, font=FONT_BODY, bg=BG3, fg=TEXT,
                     insertbackground=CYAN, bd=0, relief="flat",
                     disabledbackground=BG3, disabledforeground=TEXT2)
        e.insert(0, placeholder_or_value)

        if readonly:
            e.configure(state="disabled")

        # Underline focus effect
        line = tk.Frame(f, bg=BORDER, height=1)
        line.pack(fill="x")

        e.bind("<FocusIn>",  lambda ev: line.configure(bg=CYAN))
        e.bind("<FocusOut>", lambda ev: line.configure(bg=BORDER))
        e.pack(fill="x", ipady=7, pady=(2, 0))
        return e

    def _popup_btn(self, parent, text, color, cmd):
        btn = tk.Button(parent, text=text,
                        font=("Courier New", 10, "bold"),
                        bg=color, fg=BG,
                        bd=0, pady=11, cursor="hand2",
                        activebackground=WHITE, activeforeground=BG,
                        command=cmd)
        btn.pack(fill="x", padx=28, pady=(14, 0))
        return btn

    # ══════════════════════════════════════════════════════════
    #  REGISTER STUDENT
    # ══════════════════════════════════════════════════════════
    def open_register(self) -> None:
        """Open student registration dialog."""
        win = self._make_popup("Register New Student", 440, 360)
        self._popup_title(win, "REGISTER NEW STUDENT",
                          "Fill in details, then face the camera for 20 seconds.")
        tk.Frame(win, bg=BORDER, height=1).pack(fill="x", padx=28, pady=(10, 0))

        e_name = self._field(win, "Full Name",   "e.g. Sabin Katwal")
        e_roll = self._field(win, "Roll Number", "e.g. BCA-101")
        e_dept = self._field(win, "Department",  "e.g. Computer Science")

        placeholders = {
            e_name: "e.g. Sabin Katwal",
            e_roll: "e.g. BCA-101",
            e_dept: "e.g. Computer Science"
        }

        def submit():
            name = e_name.get().strip()
            roll = e_roll.get().strip()
            dept = e_dept.get().strip()
            
            # Remove placeholder values
            for e, ph in placeholders.items():
                if e.get() == ph:
                    if e == e_name: name = ""
                    if e == e_roll: roll = ""
                    if e == e_dept: dept = ""
            
            # Validate inputs
            import validators as val_module
            valid, msg = val_module.validate_student_input(name, roll, dept)
            if not valid:
                messagebox.showerror("Validation Error", msg, parent=win)
                return
            
            win.destroy()
            def run():
                self._set_status("REGISTERING", CYAN)
                self._log(f"Registering: {name}  [{roll}]", "SYS")
                try:
                    import register_student
                    sid = register_student.register_student(name, dept, roll)
                    if sid:
                        self._log(f"✅ {name} registered (ID: {sid}).", "OK")
                        # Optionally auto-run face encoding to include the new student
                        try:
                            if getattr(config, "AUTO_UPDATE_MODEL_AFTER_REGISTER", False):
                                self._log("Auto updating face model...", "SYS")
                                self.run_encoding()
                        except Exception as e:
                            logger.error(f"Failed to auto-update model: {e}")
                    else:
                        self._log(f"❌ Registration failed for {name}.", "ERR")
                except Exception as e:
                    logger.error(f"Registration error: {e}")
                    self._log(f"❌ Registration error: {e}", "ERR")
                finally:
                    self._set_status("STANDBY")
                    self._refresh_stats()
            threading.Thread(target=run, daemon=True).start()

        self._popup_btn(win, "[ + ]  REGISTER + CAPTURE FACES", CYAN, submit)

    # ══════════════════════════════════════════════════════════
    #  MANAGE STUDENTS
    # ══════════════════════════════════════════════════════════
    def open_manage(self):
        win = self._make_popup("Manage Students", 860, 560)
        self._popup_title(win, "MANAGE STUDENTS",
                          "Select a student row, then choose an action.")

        # Table frame
        tf = tk.Frame(win, bg=BG2)
        tf.pack(fill="both", expand=True, padx=16, pady=10)

        style = ttk.Style()
        style.configure("M.Treeview",
                        background=BG2, foreground=TEXT,
                        fieldbackground=BG2,
                        font=("Courier New", 9),
                        rowheight=30, borderwidth=0)
        style.configure("M.Treeview.Heading",
                        background=BG3, foreground=CYAN,
                        font=("Courier New", 8, "bold"),
                        borderwidth=0, relief="flat")
        style.map("M.Treeview",
                  background=[("selected", "#0f2a38")],
                  foreground=[("selected", CYAN)])

        cols = ("ID", "Roll No", "Name", "Department", "Enrolled", "Photos")
        tree = ttk.Treeview(tf, columns=cols, show="headings",
                            style="M.Treeview", height=13)
        for col, w, anch in zip(cols,
                                 [50, 100, 200, 160, 110, 90],
                                 ["center","center","w","w","center","center"]):
            tree.heading(col, text=col.upper())
            tree.column(col, width=w, anchor=anch)

        sb = tk.Scrollbar(tf, bg=BG3, troughcolor=BG,
                          activebackground=CYAN, bd=0, width=8,
                          command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # ── Helpers ──
        def photo_count(sid, name):
            folder = os.path.join("dataset", f"{sid}_{name.replace(' ','_')}")
            if os.path.isdir(folder):
                return len([f for f in os.listdir(folder)
                            if f.lower().endswith((".jpg",".jpeg",".png"))])
            return 0

        def load():
            for i in tree.get_children(): tree.delete(i)
            try:
                conn = get_conn(); c = conn.cursor()
                c.execute("SELECT student_id,roll_number,name,department,enrolled_date FROM students ORDER BY student_id")
                for i, row in enumerate(c.fetchall()):
                    pc  = photo_count(row[0], row[2])
                    tag = "even" if i % 2 == 0 else "odd"
                    tree.insert("", "end", iid=str(row[0]),
                                values=(row[0], row[1], row[2], row[3], str(row[4]), f"{pc}"),
                                tags=(tag,))
                tree.tag_configure("even", background=BG2)
                tree.tag_configure("odd",  background=BG3)
                conn.close()
            except Exception as e:
                messagebox.showerror("DB Error", str(e), parent=win)

        load()

        def get_sel():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("No Selection",
                                       "Select a student row first.", parent=win)
                return None, None, None, None
            v = tree.item(sel[0], "values")
            return v[0], v[2], v[1], v[3]  # id, name, roll, dept

        # ── EDIT ──────────────────────────────────────────
        def edit():
            sid, name, roll, dept = get_sel()
            if sid is None: return

            ew = self._make_popup("Edit Student", 420, 330)
            self._popup_title(ew, "EDIT STUDENT", f"Editing: {name}")
            tk.Frame(ew, bg=BORDER, height=1).pack(fill="x", padx=28, pady=(8,0))

            ef_name = self._field(ew, "Full Name",   name)
            ef_roll = self._field(ew, "Roll Number", roll)
            ef_dept = self._field(ew, "Department",  dept)

            def save():
                nn = ef_name.get().strip()
                nr = ef_roll.get().strip()
                nd = ef_dept.get().strip()
                if not nn or not nr:
                    messagebox.showerror("Error", "Name and Roll Number required!", parent=ew)
                    return
                try:
                    old_f = os.path.join("dataset", f"{sid}_{name.replace(' ','_')}")
                    new_f = os.path.join("dataset", f"{sid}_{nn.replace(' ','_')}")
                    if os.path.isdir(old_f) and old_f != new_f:
                        os.rename(old_f, new_f)
                        self._log(f"📁 Folder renamed → {new_f}", "SYS")

                    conn = get_conn(); c = conn.cursor()
                    c.execute("UPDATE students SET name=%s,roll_number=%s,department=%s WHERE student_id=%s",
                              (nn, nr, nd, sid))
                    conn.commit(); conn.close()
                    self._log(f"✅ Updated: {name} → {nn}", "OK")
                    ew.destroy(); load(); self._refresh_stats()
                except Exception as e:
                    messagebox.showerror("Error", str(e), parent=ew)

            self._popup_btn(ew, "[ ✓ ]  SAVE CHANGES", GREEN, save)

        # ── DELETE PHOTOS ──────────────────────────────────
        def delete_photos():
            sid, name, roll, _ = get_sel()
            if sid is None: return
            folder = os.path.join("dataset", f"{sid}_{name.replace(' ','_')}")
            if not os.path.isdir(folder):
                messagebox.showinfo("Not Found",
                                    f"No photo folder for {name}.", parent=win)
                return
            count = photo_count(sid, name)
            if not messagebox.askyesno("Delete Photos",
                    f"Delete all {count} photos for:\n\n"
                    f"  {name}  (Roll: {roll})\n\n"
                    "You will need to re-register their face.\nContinue?", parent=win):
                return
            try:
                shutil.rmtree(folder)
                os.makedirs(folder)
                self._log(f"🗑 {count} photos deleted for {name}.", "SYS")
                messagebox.showinfo("Done",
                    f"Deleted {count} photos.\nRun Update Face Model to rebuild.", parent=win)
                load()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)

        # ── DELETE STUDENT ─────────────────────────────────
        def delete_student():
            sid, name, roll, _ = get_sel()
            if sid is None: return
            if not messagebox.askyesno("⚠ Delete Student",
                    f"Permanently delete:\n\n  {name}  (Roll: {roll})\n\n"
                    "Removes attendance records + photos.\nCANNOT be undone. Continue?",
                    parent=win):
                return
            try:
                folder = os.path.join("dataset", f"{sid}_{name.replace(' ','_')}")
                if os.path.isdir(folder):
                    shutil.rmtree(folder)

                conn = get_conn(); c = conn.cursor()
                c.execute("DELETE FROM attendance WHERE student_id=%s", (sid,))
                c.execute("DELETE FROM students WHERE student_id=%s", (sid,))
                conn.commit(); conn.close()

                self._log(f"✅ Student '{name}' permanently deleted.", "OK")
                messagebox.showinfo("Deleted",
                    f"'{name}' removed.\nRun Update Face Model to rebuild.", parent=win)
                load(); self._refresh_stats()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)

        # ── Button bar ─────────────────────────────────────
        bbar = tk.Frame(win, bg=BG)
        bbar.pack(fill="x", padx=16, pady=(0, 14))

        for text, color, cmd in [
            ("[ ✏ ]  EDIT",            CYAN,   edit),
            ("[ 📷 ]  DELETE PHOTOS",  AMBER,  delete_photos),
            ("[ 🗑 ]  DELETE STUDENT", RED,    delete_student),
        ]:
            b = tk.Button(bbar, text=text,
                          font=("Courier New", 9, "bold"),
                          bg=BG3, fg=color,
                          bd=0, padx=16, pady=9, cursor="hand2",
                          activebackground=BG2, activeforeground=WHITE,
                          command=cmd)
            b.pack(side="left", padx=(0, 8))

        tk.Button(bbar, text="[ ⟳ ]  REFRESH",
                  font=("Courier New", 9), bg=BG3, fg=TEXT2,
                  bd=0, padx=14, pady=9, cursor="hand2",
                  activebackground=BG2, activeforeground=TEXT,
                  command=load).pack(side="right")


# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = AttendanceApp(root)
        logger.info("Application started")
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Fatal application error: {e}")
        raise