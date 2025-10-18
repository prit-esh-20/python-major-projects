import tkinter as tk
from tkinter import messagebox
from reportlab.pdfgen import canvas
import datetime

# Login credentials
USERNAME = "admin"
PASSWORD = "1234"

inventory = {
    'Rice (1kg)': [50, 50],       
    'Wheat (1kg)': [40, 50],
    'Sugar (1kg)': [45, 50],
    'Milk (1L)': [30, 50],
    'Eggs (6)': [36, 50],
    'Soap': [25, 50],
    'Shampoo (200ml)': [90, 50],
    'Toothpaste (100g)': [35, 50]
}


class GroceryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grocery Store")
        self.root.geometry("700x600")
        self.theme = 'light'

        self.cart = {}
        self.entries = {}
        self.bg_colors = {'light': 'lightyellow', 'dark': '#2c2c2c'}
        self.fg_colors = {'light': 'black', 'dark': 'white'}

        self.setup_ui()

    def setup_ui(self):
        self.root.configure(bg=self.bg_colors[self.theme])
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="🛒 Grocery Store", font=("Arial", 18, "bold"),
                 bg=self.bg_colors[self.theme], fg=self.fg_colors[self.theme]).pack(pady=10)

        self.items_frame = tk.Frame(self.root, bg=self.bg_colors[self.theme])
        self.items_frame.pack(pady=10)

        for i, (item, (price, stock)) in enumerate(inventory.items()):
            tk.Label(self.items_frame, text=f"{item} - ₹{price} ({stock} left)", font=("Arial", 12),
                     bg=self.bg_colors[self.theme], fg=self.fg_colors[self.theme]).grid(row=i, column=0, sticky='w', padx=10, pady=5)
            entry = tk.Entry(self.items_frame, width=5)
            entry.grid(row=i, column=1)
            self.entries[item] = entry

        self.button_frame = tk.Frame(self.root, bg=self.bg_colors[self.theme])
        self.button_frame.pack(pady=10)
        

        tk.Button(self.button_frame, text="Add to Cart", command=self.add_to_cart, bg='green', fg='white', width=15).grid(row=0, column=0, padx=5)
        tk.Button(self.button_frame, text="Generate PDF Bill", command=self.generate_pdf_bill, bg='blue', fg='white', width=18).grid(row=0, column=1, padx=5)
        tk.Button(self.button_frame, text="Clear", command=self.clear_cart, bg='red', fg='white', width=12).grid(row=0, column=2, padx=5)
        tk.Button(self.button_frame, text="Toggle Theme", command=self.toggle_theme, bg='gray', fg='white', width=15).grid(row=0, column=3, padx=5)

        self.bill_area = tk.Text(self.root, height=15, width=70, bg=self.bg_colors[self.theme], fg=self.fg_colors[self.theme], font=("Courier", 10))
        self.bill_area.pack(pady=10)

    def add_to_cart(self):
        for item, entry in self.entries.items():
            qty = entry.get()
            if qty.isdigit() and int(qty) > 0:
                qty = int(qty)
                available = inventory[item][1]
                if qty <= available:
                    self.cart[item] = qty
                else:
                    messagebox.showwarning("Out of Stock", f"Only {available} of {item} left")
        messagebox.showinfo("Success", "Items added to cart!")

    def generate_pdf_bill(self):
        if not self.cart:
            messagebox.showwarning("Empty", "Cart is empty!")
            return

        now = datetime.datetime.now()
        filename = f"Bill_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
        c = canvas.Canvas(filename)

        y = 800
        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, y, "Pritesh Grocery Store Bill")
        y -= 40

        c.setFont("Helvetica", 12)
        c.drawString(50, y, "Item")
        c.drawString(250, y, "Qty")
        c.drawString(350, y, "Price")
        y -= 20
        c.line(50, y, 500, y)
        y -= 20

        total = 0
        self.bill_area.delete('1.0', tk.END)
        self.bill_area.insert(tk.END, "         Pritesh Grocery Store\n")
        self.bill_area.insert(tk.END, "         ----------------------\n")
        self.bill_area.insert(tk.END, f"{'Item':20}{'Qty':>5}{'Price':>10}\n")
        self.bill_area.insert(tk.END, f"{'-'*35}\n")

        for item, qty in self.cart.items():
            price = inventory[item][0] * qty
            total += price
            inventory[item][1] -= qty  # reduce stock
            self.bill_area.insert(tk.END, f"{item:20}{qty:>5}{price:>10}\n")

            c.drawString(50, y, item)
            c.drawString(250, y, str(qty))
            c.drawString(350, y, f"₹{price}")
            y -= 20

        c.line(50, y, 500, y)
        y -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"Total: ₹{total}")
        c.save()

        self.bill_area.insert(tk.END, f"{'-'*35}\n")
        self.bill_area.insert(tk.END, f"{'Total':25}₹{total:>8}\n")
        self.bill_area.insert(tk.END, f"{'-'*35}\n")
        messagebox.showinfo("Bill Generated", f"PDF saved as {filename}")
        self.setup_ui()  # refresh stock display

    def clear_cart(self):
        self.cart.clear()
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.bill_area.delete('1.0', tk.END)

    def toggle_theme(self):
        self.theme = 'dark' if self.theme == 'light' else 'light'
        self.setup_ui()


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Grocery Store")
        self.root.geometry("400x250")
        self.root.configure(bg='white')

        tk.Label(root, text="Login", font=("Arial", 18, "bold"), bg='white').pack(pady=10)
        tk.Label(root, text="Username:", bg='white').pack()
        self.user_entry = tk.Entry(root)
        self.user_entry.pack(pady=5)

        tk.Label(root, text="Password:", bg='white').pack()
        self.pass_entry = tk.Entry(root, show='*')
        self.pass_entry.pack(pady=5)

        tk.Button(root, text="Login", command=self.check_login, bg='green', fg='white').pack(pady=15)

    def check_login(self):
        if self.user_entry.get() == USERNAME and self.pass_entry.get() == PASSWORD:
            self.root.destroy()
            main_app = tk.Tk()
            GroceryApp(main_app)
            main_app.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password!")


# Launch login first
if __name__ == "__main__":
    login_root = tk.Tk()
    LoginWindow(login_root)
    login_root.mainloop()
