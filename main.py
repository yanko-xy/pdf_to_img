import fitz  # PyMuPDF
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# 将PDF的某一页转换为图像


def pdf_page_to_image(pdf_path, page_num):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(page_num)
    pix = page.get_pixmap()
    image_path = f"page_{page_num + 1}.png"
    pix.save(image_path)
    return image_path

# 裁剪图像（纵向）


def crop_image_vertically(image_path, cut_position, scale_ratio, page_num):
    global cropped_images
    image = Image.open(image_path)
    width, height = image.size

    # 根据缩放比例调整裁剪位置
    cut_position_original = int(cut_position * scale_ratio)

    # 裁剪左半部分
    left_part = image.crop((0, 0, cut_position_original, height))
    left_part_path = f"left_page_{page_num + 1}.png"
    left_part.save(left_part_path)

    # 裁剪右半部分
    right_part = image.crop((cut_position_original, 0, width, height))
    right_part_path = f"right_page_{page_num + 1}.png"
    right_part.save(right_part_path)

    # 将裁剪后的图片路径添加到列表
    cropped_images.extend([left_part_path, right_part_path])

    print(f"第 {page_num + 1} 页图像已切割并保存为：left_page_{page_num + 1}.png 和 right_page_{page_num + 1}.png")

# 裁剪图像（横向）


def crop_image_horizontally(image_path, cut_position, scale_ratio, page_num):
    global cropped_images, tag
    image = Image.open(image_path)
    width, height = image.size

    # 根据缩放比例调整裁剪位置
    cut_position_original = int(cut_position * scale_ratio)

    # 裁剪上半部分
    top_part = image.crop((0, 0, width, cut_position_original))
    top_part_path = f"top_page_{page_num + 1}_{tag}.png"
    top_part.save(top_part_path)

    # 裁剪下半部分
    bottom_part = image.crop((0, cut_position_original, width, height))
    bottom_part_path = f"bottom_page_{page_num + 1}_{tag}.png"
    bottom_part.save(bottom_part_path)

    # 将裁剪后的图片路径添加到列表
    cropped_images.extend([top_part_path, bottom_part_path])

    print(f"第 {page_num + 1} 页图像已切割并保存为：top_page_{page_num + 1}_{tag}.png 和 bottom_page_{page_num + 1}_{tag}.png")

    tag += 1
    return top_part_path, bottom_part_path

# 鼠标移动时更新辅助线


def on_mouse_move(event):
    global is_tab_pressed
    canvas.delete("line")

    if is_tab_pressed:
        # 横向辅助线
        canvas.create_line(0, event.y, canvas.winfo_width(),
                           event.y, fill="red", tags="line")
    else:
        # 纵向辅助线
        canvas.create_line(event.x, 0, event.x,
                           canvas.winfo_height(), fill="red", tags="line")

# 鼠标点击事件处理，进行图像裁剪


def on_click(event):
    global image_path, scale_ratio, current_page, total_pages, is_tab_pressed, horizontal_crop_mode, next_part, tag

    if is_tab_pressed:
        # 进行横向裁剪
        cut_position = event.y  # 获取鼠标点击的 y 坐标，作为切割位置
        if not horizontal_crop_mode:
            top_part_path, bottom_part_path = crop_image_horizontally(
                image_path, cut_position, scale_ratio, current_page)
            next_part = [top_part_path, bottom_part_path]
            load_image(next_part[0])  # 加载上半部分
            horizontal_crop_mode = True  # 进入切割上/下部分的模式
        else:
            # 第二次裁剪时加载下半部分
            next_part.extend()
            if next_part:
                next_part.pop(0)
                if next_part:
                    load_image(next_part[0])
                else:
                    horizontal_crop_mode = False
                    if current_page < total_pages - 1:
                        current_page += 1
                        load_page()
                    else:
                        messagebox.showinfo("裁剪完成", "所有页面都已裁剪完毕！")
    else:
        # 进行纵向裁剪，完成后加载下一页
        cut_position = event.x  # 获取鼠标点击的 x 坐标，作为切割位置
        crop_image_vertically(image_path, cut_position,
                              scale_ratio, current_page)

        if next_part:
            next_part.pop(0)
            if next_part:
                load_image(next_part[0])
            else:
                horizontal_crop_mode = False
                if current_page < total_pages - 1:
                    current_page += 1
                    load_page()
                else:

                    messagebox.showinfo("裁剪完成", "所有页面都已裁剪完毕！")

        # 加载下一页
        elif current_page < total_pages - 1:
            tag = 1
            current_page += 1
            load_page()
        else:
            save_images_as_pdf()
            messagebox.showinfo("裁剪完成", "所有页面都已裁剪完毕！")

# 加载PDF的指定页并显示在窗口中


def load_page():
    global image_path, img_tk, scale_ratio, current_page, total_pages, horizontal_crop_mode, images
    horizontal_crop_mode = False  # 重置横向裁剪模式
    image_path = pdf_page_to_image(pdf_path, current_page)
    images.extend([image_path])
    load_image(image_path)


def load_image(image_path):
    global img_tk, scale_ratio
    # 打开图像并记录原始尺寸
    img = Image.open(image_path)
    original_width, original_height = img.size

    # 设置最大宽度和高度，缩放图片
    max_width, max_height = 800, 600
    img.thumbnail((max_width, max_height))  # 保持比例缩放

    # 计算缩放比例
    scale_ratio = original_width / img.width

    # 将调整后的图像转换为 Tkinter 格式
    img_tk = ImageTk.PhotoImage(img)

    # 清除画布上的内容并显示新的图像
    canvas.delete("all")
    canvas.create_image(0, 0, anchor="nw", image=img_tk)
    canvas.config(width=img_tk.width(), height=img_tk.height())

# 加载PDF并开始依次处理每一页


def load_pdf():
    global pdf_path, total_pages, current_page
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])

    if pdf_path:
        pdf_document = fitz.open(pdf_path)
        total_pages = pdf_document.page_count  # 获取PDF总页数
        current_page = 0  # 从第一页开始
        load_page()

# 将裁剪后的图片保存为 PDF


def save_images_as_pdf():
    global cropped_images, pdf_path, images
    if not cropped_images:
        messagebox.showwarning("警告", "没有裁剪后的图像可保存为PDF！")
        return

    # 打开第一张图片，作为 PDF 的起始页面
    first_image = Image.open(cropped_images[0])
    first_image = first_image.convert('RGB')

    # 其余的图像
    image_list = [Image.open(img).convert('RGB') for img in cropped_images[1:]]

    list = pdf_path.split(".")
    # 保存为 PDF
    first_image.save(f"{list[0]}_img.pdf",
                     save_all=True, append_images=image_list)
    messagebox.showinfo("保存成功", f"PDF已保存至：{list[0]}_img.pdf")

    for i in range(len(cropped_images)):
        os.remove(cropped_images[i])

    for i in range(len(images)):
        os.remove(images[i])


# 键盘事件处理：按下 Tab 键切换为横向辅助线，松开 Tab 键恢复为纵向


def on_tab_press(event):
    global is_tab_pressed
    is_tab_pressed = True


def on_tab_release(event):
    global is_tab_pressed
    is_tab_pressed = False


# 初始化 tkinter 窗口
root = tk.Tk()
root.title("PDF逐页裁剪工具")


# 创建画布来显示PDF页面和辅助线
canvas = tk.Canvas(root)
canvas.pack()

# 绑定鼠标移动和点击事件
canvas.bind("<Motion>", on_mouse_move)  # 鼠标移动时画辅助线
canvas.bind("<Button-1>", on_click)     # 鼠标点击时裁剪图像

# 绑定 Tab 键的按下和释放事件
root.bind("<Tab>", on_tab_press)
root.bind("<KeyRelease-Tab>", on_tab_release)

# 添加一个按钮来加载PDF
button = tk.Button(root, text="加载PDF", command=load_pdf)
button.pack()

# 定义全局变量
scale_ratio = 1.0
current_page = 0
total_pages = 0
pdf_path = ""
is_tab_pressed = False  # 用于记录 Tab 键是否被按下
horizontal_crop_mode = False  # 用于记录是否处于横向裁剪后的再裁剪模式
next_part = []  # 存储横向裁剪后的上半部分和下半部分的图片路径
cropped_images = []
images = []
tag = 1


# 启动 tkinter 循环
root.mainloop()
