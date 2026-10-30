"""Учебное приложение «Мир пряжи»."""
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3, os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
DB = ROOT / "databases" / "mir_pryazhi.db"
IMG = ROOT / "resources"
BG, SECONDARY, ACCENT, LOW = "#FFFFFF", "#D2F6E7", "#70B2AF", "#ff8080"

def connect():
    c = sqlite3.connect(DB); c.execute("PRAGMA foreign_keys=ON"); return c

def money(v): return f"{v:.2f} руб."

class App:
    def __init__(self, root):
        self.root=root; root.title("Система продаж — Мир пряжи"); root.geometry("1100x760"); root.configure(bg=BG)
        try: root.iconbitmap(IMG/"Мир пряжи.ico")
        except Exception: pass
        self.user=None; self.cart={}; self.photos=[]
        self.build(); self.load_catalog()

    def build(self):
        head=tk.Frame(self.root,bg=SECONDARY,height=88); head.pack(fill="x"); head.pack_propagate(False)
        try:
            from PIL import Image, ImageTk
            im=Image.open(IMG/"Мир пряжи.png"); im.thumbnail((170,70)); self.logo=ImageTk.PhotoImage(im)
            tk.Label(head,image=self.logo,bg=SECONDARY).pack(side="left",padx=15)
        except Exception: tk.Label(head,text="🧶 МИР ПРЯЖИ",font=("Calibri",22,"bold"),bg=SECONDARY).pack(side="left",padx=18)
        tk.Label(head,text="КАТАЛОГ ПРЯЖИ",font=("Calibri",20,"bold"),bg=SECONDARY).pack(side="left",expand=True)
        self.user_lbl=tk.Label(head,text="Гость",bg=SECONDARY,font=("Calibri",11)); self.user_lbl.pack(side="right",padx=15)
        bar=tk.Frame(self.root,bg=BG); bar.pack(fill="x",padx=15,pady=10)
        tk.Label(bar,text="Поиск:",bg=BG).pack(side="left")
        self.search=tk.StringVar(); e=tk.Entry(bar,textvariable=self.search,width=25); e.pack(side="left",padx=5); self.search.trace_add("write",lambda *_:self.load_catalog())
        tk.Label(bar,text="Категория:",bg=BG).pack(side="left",padx=(15,3))
        self.category=tk.StringVar(value="Все категории")
        self.catbox=ttk.Combobox(bar,textvariable=self.category,state="readonly",width=25); self.catbox.pack(side="left")
        self.catbox.bind("<<ComboboxSelected>>",lambda e:self.load_catalog())
        tk.Label(bar,text="Сортировка:",bg=BG).pack(side="left",padx=(15,3))
        self.sort=tk.StringVar(value="По возрастанию цены")
        sb=ttk.Combobox(bar,textvariable=self.sort,state="readonly",values=["По возрастанию цены","По убыванию цены"],width=24); sb.pack(side="left")
        sb.bind("<<ComboboxSelected>>",lambda e:self.load_catalog())
        self.login_btn=tk.Button(bar,text="Войти",command=self.login,bg=ACCENT,relief="flat"); self.login_btn.pack(side="right",padx=4)
        self.logout_btn=tk.Button(bar,text="Выйти",command=self.logout,bg=SECONDARY,relief="flat",state="disabled"); self.logout_btn.pack(side="right",padx=4)
        self.cart_btn=tk.Button(bar,text="Корзина (0)",command=self.show_cart,bg=ACCENT,relief="flat",state="disabled"); self.cart_btn.pack(side="right",padx=4)
        self.orders_btn=tk.Button(bar,text="Заказы",command=self.show_orders,bg=SECONDARY,relief="flat",state="disabled"); self.orders_btn.pack(side="right",padx=4)
        self.canvas=tk.Canvas(self.root,bg=BG,highlightthickness=0); scr=ttk.Scrollbar(self.root,orient="vertical",command=self.canvas.yview)
        self.list=tk.Frame(self.canvas,bg=BG); self.list.bind("<Configure>",lambda e:self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0,0),window=self.list,anchor="nw"); self.canvas.configure(yscrollcommand=scr.set)
        self.canvas.pack(side="left",fill="both",expand=True,padx=(10,0)); scr.pack(side="right",fill="y")
        self.catbox["values"]=["Все категории"]+self.categories()
    def categories(self):
        with connect() as c:return [x[0] for x in c.execute("select distinct category from models order by category")]
    def load_catalog(self):
        if not hasattr(self,"list"): return
        for w in self.list.winfo_children():w.destroy()
        q=self.search.get().strip() if hasattr(self,"search") else ""
        cat=self.category.get() if hasattr(self,"category") else "Все категории"
        order="ASC" if self.sort.get()=="По возрастанию цены" else "DESC"
        sql="""SELECT m.id,m.name,m.manufacturer,m.category,m.subcategory,m.description,m.composition,m.base_price,m.image,
        COALESCE(SUM(s.quantity),0) FROM models m LEFT JOIN stock s ON s.model_id=m.id WHERE (m.name LIKE ? OR m.manufacturer LIKE ?)"""
        args=[f"%{q}%",f"%{q}%"]
        if cat!="Все категории":sql+=" AND m.category=?";args.append(cat)
        sql+=f" GROUP BY m.id ORDER BY m.base_price {order}"
        with connect() as c: rows=c.execute(sql,args).fetchall()
        for m in rows:self.card(m)
    def card(self,m):
        mid,name,man,cat,sub,desc,comp,price,img,qty=m
        color=LOW if qty<=3 else BG
        f=tk.Frame(self.list,bg=color,bd=1,relief="solid");f.pack(fill="x",padx=8,pady=5)
        try:
            from PIL import Image,ImageTk
            p=IMG/"Images"/(img or "")
            if not img or not p.exists():p=IMG/"picture.png"
            im=Image.open(p); im.thumbnail((115,115)); ph=ImageTk.PhotoImage(im); self.photos.append(ph)
            tk.Label(f,image=ph,bg=color).pack(side="left",padx=12,pady=10)
        except Exception:tk.Label(f,text="Нет фото",width=14,height=6,bg=color).pack(side="left",padx=12)
        txt=tk.Frame(f,bg=color);txt.pack(side="left",fill="both",expand=True,padx=8,pady=8)
        tk.Label(txt,text=f"{name} — {man}",font=("Calibri",15,"bold"),bg=color,anchor="w").pack(fill="x")
        tk.Label(txt,text=f"{cat} / {sub}   •   {comp}",bg=color,anchor="w",wraplength=700).pack(fill="x",pady=2)
        tk.Label(txt,text=desc,bg=color,anchor="w",wraplength=700).pack(fill="x")
        tk.Label(txt,text=f"В наличии: {qty} мотков     Цена от {money(price)}",font=("Calibri",12,"bold"),bg=color,anchor="w").pack(fill="x",pady=4)
        tk.Button(f,text="Выбрать вариант",bg=ACCENT,relief="flat",command=lambda:self.choose(mid,name)).pack(side="right",padx=15,pady=15)
    def login(self):
        win=tk.Toplevel(self.root);win.title("Авторизация");win.geometry("350x190");win.transient(self.root);win.grab_set()
        tk.Label(win,text="Введите логин из списка пользователей",wraplength=300).pack(pady=12)
        v=tk.StringVar();ent=tk.Entry(win,textvariable=v,width=28);ent.pack();ent.focus()
        def go():
            with connect() as c:u=c.execute("select u.id,u.surname,u.first_name,u.patronymic,u.login,r.name from users u join roles r on r.id=u.role_id where u.login=?",(v.get().strip(),)).fetchone()
            if not u:messagebox.showerror("Вход","Пользователь не найден");return
            self.user=u;self.user_lbl.config(text=f"{u[1]} {u[2]} ({u[5]})");self.logout_btn.config(state="normal");self.login_btn.config(state="disabled")
            self.cart_btn.config(state="normal" if u[5]!="Гость" else "disabled")
            self.orders_btn.config(state="normal" if u[5] in ("Менеджер","Администратор") else "disabled")
            win.destroy()
        tk.Button(win,text="Войти",command=go,bg=ACCENT).pack(pady=12);tk.Label(win,text="Примеры: admin, manager1, client01",fg="gray").pack()
    def logout(self):
        self.user=None;self.cart.clear();self.update_cart_btn();self.user_lbl.config(text="Гость")
        self.login_btn.config(state="normal");self.logout_btn.config(state="disabled");self.cart_btn.config(state="disabled");self.orders_btn.config(state="disabled")
    def choose(self,mid,name):
        with connect() as c:variants=c.execute("select id,variant,quantity,price from stock where model_id=? order by variant",(mid,)).fetchall()
        w=tk.Toplevel(self.root);w.title(name);w.geometry("420x330");w.transient(self.root)
        tk.Label(w,text=name,font=("Calibri",16,"bold")).pack(pady=12)
        v=tk.StringVar(); vals=[f"{x[1]} — {x[2]} мотков — {money(x[3])}" for x in variants]
        box=ttk.Combobox(w,values=vals,state="readonly",textvariable=v,width=42);box.pack(pady=8)
        if vals:box.current(0)
        tk.Label(w,text="Количество мотков:").pack(pady=(12,2));q=tk.StringVar(value="1");tk.Entry(w,textvariable=q,width=10).pack()
        def add():
            if not self.user:messagebox.showwarning("Авторизация","Войдите, чтобы добавить товар в корзину");return
            try:n=int(q.get());assert n>0
            except:messagebox.showerror("Количество","Введите положительное целое число");return
            if not box.current(): idx=0
            else:idx=box.current()
            s=variants[idx]
            current=self.cart.get(s[0],0)
            if n+current>s[2]:messagebox.showwarning("Остаток",f"Доступно {s[2]} мотков");return
            self.cart[s[0]]=current+n;self.update_cart_btn();w.destroy()
        tk.Button(w,text="Добавить в корзину",command=add,bg=ACCENT).pack(pady=18)
    def update_cart_btn(self):self.cart_btn.config(text=f"Корзина ({sum(self.cart.values())})")
    def show_cart(self):
        w=tk.Toplevel(self.root);w.title("Корзина");w.geometry("700x480")
        tree=ttk.Treeview(w,columns=("name","variant","qty","price"),show="headings")
        for k,t in [("name","Товар"),("variant","Цвет"),("qty","Мотков"),("price","Цена")]:tree.heading(k,text=t)
        tree.pack(fill="both",expand=True,padx=10,pady=10)
        def reload():
            tree.delete(*tree.get_children())
            with connect() as c:
                for sid,n in self.cart.items():
                    r=c.execute("select m.name,s.variant,s.quantity,s.price from stock s join models m on m.id=s.model_id where s.id=?",(sid,)).fetchone()
                    if r:tree.insert("","end",iid=str(sid),values=(r[0],r[1],n,money(r[3])))
        def remove():
            sel=tree.selection()
            if sel:self.cart.pop(int(sel[0]),None);reload();self.update_cart_btn()
        def checkout():
            if not self.cart:messagebox.showinfo("Корзина","Корзина пуста");return
            with connect() as c:
                try:
                    c.execute("BEGIN IMMEDIATE")
                    for sid,n in self.cart.items():
                        row=c.execute("select quantity from stock where id=?",(sid,)).fetchone()
                        if not row or row[0]<n:raise ValueError("Остаток изменился. Обновите корзину.")
                    client=f"{self.user[1]} {self.user[2]} {self.user[3] or ''}".strip()
                    cur=c.execute("insert into orders(order_date,client) values(?,?)",(datetime.now().strftime("%Y-%m-%d"),client));oid=cur.lastrowid
                    for sid,n in self.cart.items():
                        price=c.execute("select price from stock where id=?",(sid,)).fetchone()[0]
                        c.execute("insert into order_items(order_id,stock_id,quantity,unit_price) values(?,?,?,?)",(oid,sid,n,price))
                        c.execute("update stock set quantity=quantity-? where id=?",(n,sid))
                    c.commit()
                except Exception as e:c.rollback();messagebox.showerror("Заказ",str(e));return
            self.cart.clear();self.update_cart_btn();w.destroy();self.load_catalog();messagebox.showinfo("Заказ",f"Заказ №{oid} оформлен")
        bar=tk.Frame(w);bar.pack(fill="x",pady=8)
        tk.Button(bar,text="Удалить позицию",command=remove).pack(side="left",padx=8)
        tk.Button(bar,text="Оформить заказ",command=checkout,bg=ACCENT).pack(side="left",padx=8)
        tk.Button(bar,text="Закрыть",command=w.destroy).pack(side="right",padx=8)
        reload()
    def show_orders(self):
        w=tk.Toplevel(self.root);w.title("Заказы");w.geometry("850x500")
        tree=ttk.Treeview(w,columns=("id","date","client","sum"),show="headings")
        for k,t,width in [("id","№",55),("date","Дата",120),("client","Клиент",400),("sum","Сумма",130)]:tree.heading(k,text=t);tree.column(k,width=width)
        tree.pack(fill="both",expand=True,padx=12,pady=12)
        def load():
            tree.delete(*tree.get_children())
            with connect() as c:
                for r in c.execute("""select o.id,o.order_date,o.client,coalesce(sum(i.quantity*i.unit_price),0) from orders o left join order_items i on i.order_id=o.id group by o.id order by o.id desc"""):
                    tree.insert("","end",iid=str(r[0]),values=(r[0],datetime.strptime(r[1],"%Y-%m-%d").strftime("%d.%m.%Y"),r[2],money(r[3])))
        def detail():
            sel=tree.selection()
            if not sel:return
            oid=int(sel[0]);self.order_detail(oid,load)
        bar=tk.Frame(w);bar.pack(fill="x",pady=8)
        tk.Button(bar,text="Состав заказа",command=detail,bg=ACCENT).pack(side="left",padx=8)
        if self.user[5] in ("Менеджер","Администратор"):
            tk.Button(bar,text="Удалить заказ",command=lambda:self.delete_order(tree,load)).pack(side="left",padx=8)
        tk.Button(bar,text="Обновить",command=load).pack(side="left")
        load()
    def order_detail(self,oid,refresh):
        w=tk.Toplevel(self.root);w.title(f"Состав заказа №{oid}");w.geometry("800x440")
        tree=ttk.Treeview(w,columns=("name","maker","variant","qty","price","total"),show="headings")
        for k,t in [("name","Товар"),("maker","Производство"),("variant","Цвет"),("qty","Количество"),("price","Цена"),("total","Итого")]:tree.heading(k,text=t)
        tree.pack(fill="both",expand=True,padx=10,pady=10)
        with connect() as c:
            o=c.execute("select order_date,client from orders where id=?",(oid,)).fetchone()
            rows=c.execute("""select m.name,m.manufacturer,s.variant,i.quantity,i.unit_price from order_items i join stock s on s.id=i.stock_id join models m on m.id=s.model_id where i.order_id=?""",(oid,)).fetchall()
        if o:tk.Label(w,text=f"Дата: {o[0]}    Клиент: {o[1]}").pack()
        total=0
        for r in rows:
            sm=r[3]*r[4];total+=sm;tree.insert("","end",values=(r[0],r[1],r[2],r[3],money(r[4]),money(sm)))
        tk.Label(w,text=f"ИТОГО: {money(total)}",font=("Calibri",13,"bold")).pack(pady=8)
        if self.user[5]=="Администратор":
            def setdate():
                d=date.get()
                try:datetime.strptime(d,"%Y-%m-%d")
                except:messagebox.showerror("Дата","Формат ГГГГ-ММ-ДД");return
                with connect() as c:c.execute("update orders set order_date=? where id=?",(d,oid))
                messagebox.showinfo("Дата","Дата обновлена")
            date=tk.StringVar(value=o[0]);tk.Entry(w,textvariable=date,width=13).pack(side="left",padx=12)
            tk.Button(w,text="Изменить дату",command=setdate).pack(side="left")
    def delete_order(self,tree,refresh):
        sel=tree.selection()
        if not sel:return
        oid=int(sel[0])
        if not messagebox.askyesno("Подтверждение",f"Удалить заказ №{oid}? Остатки будут восстановлены."):return
        with connect() as c:
            rows=c.execute("select stock_id,quantity from order_items where order_id=?",(oid,)).fetchall()
            for sid,n in rows:c.execute("update stock set quantity=quantity+? where id=?",(n,sid))
            c.execute("delete from orders where id=?",(oid,))
        refresh();self.load_catalog()
if __name__=="__main__":
    root=tk.Tk();App(root);root.mainloop()
