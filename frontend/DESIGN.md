# DESIGN.md — Wobbly Forms Authentication
> Trích xuất từ Stitch MCP · Project ID: `8383113126864747402`  
> Cập nhật: 2026-04-30

---

## 🎨 Bảng Màu (Color Palette)

### Brand Override Colors

| Token            | Hex       | Mô tả                            |
|-----------------|-----------|----------------------------------|
| `primary`        | `#ff4d4d` | Red Marker — CTA, nút chính      |
| `secondary`      | `#2d5da1` | Blue Pen — link, annotation      |
| `tertiary`       | `#2d2d2d` | Pencil Black — text, border      |
| `neutral`        | `#fdfbf7` | Warm Paper — nền trang           |

### Semantic Color Tokens

| Token                        | Hex         | Vai trò                          |
|-----------------------------|-------------|----------------------------------|
| `background`                 | `#fbf9f5`   | Nền toàn trang (Warm Paper)      |
| `surface`                    | `#fbf9f5`   | Bề mặt mặc định                  |
| `surface-container`          | `#efeeea`   | Card / section container         |
| `surface-container-low`      | `#f5f3ef`   | Nền nhẹ hơn                      |
| `surface-container-lowest`   | `#ffffff`   | Phần tử nổi (elevated)           |
| `surface-container-high`     | `#eae8e4`   | Sidebar / utility area           |
| `surface-container-highest`  | `#e4e2de`   | Accent surface                   |
| `surface-dim`                | `#dbdad6`   | Disabled / dimmed surface        |
| `on-surface`                 | `#1b1c1a`   | Text trên nền sáng               |
| `on-surface-variant`         | `#5b403e`   | Text phụ / muted                 |
| `outline`                    | `#8f6f6d`   | Border muted                     |
| `outline-variant`            | `#e4beba`   | Border nhẹ                       |

### Primary (Red)

| Token                   | Hex         |
|------------------------|-------------|
| `primary`               | `#b71422`   |
| `primary-container`     | `#db3237`   |
| `on-primary`            | `#ffffff`   |
| `on-primary-container`  | `#fffbff`   |
| `primary-fixed`         | `#ffdad7`   |
| `primary-fixed-dim`     | `#ffb3ae`   |
| `inverse-primary`       | `#ffb3ae`   |

### Secondary (Blue)

| Token                     | Hex         |
|--------------------------|-------------|
| `secondary`               | `#2e5ea2`   |
| `secondary-container`     | `#89b4fe`   |
| `on-secondary`            | `#ffffff`   |
| `on-secondary-container`  | `#064487`   |
| `secondary-fixed`         | `#d6e3ff`   |
| `secondary-fixed-dim`     | `#a9c7ff`   |

### Tertiary (Neutral Gray)

| Token                    | Hex         |
|-------------------------|-------------|
| `tertiary`               | `#5c5c5c`   |
| `tertiary-container`     | `#757474`   |
| `on-tertiary`            | `#ffffff`   |
| `on-tertiary-container`  | `#fffcfb`   |

### Error

| Token             | Hex         |
|------------------|-------------|
| `error`           | `#ba1a1a`   |
| `error-container` | `#ffdad6`   |
| `on-error`        | `#ffffff`   |

---

## ✍️ Kiểu Chữ (Typography)

### Font Families

| Vai trò    | Font           | Đặc điểm                               |
|-----------|----------------|----------------------------------------|
| Heading   | **Kalam**      | Chữ viết tay đậm, dạng felt-tip marker |
| Body / UI | **Patrick Hand** | Chữ viết tay sạch, dễ đọc            |

> Import từ Google Fonts:
> ```css
> @import url('https://fonts.googleapis.com/css2?family=Kalam:wght@300;400;700&family=Patrick+Hand&display=swap');
> ```

### Type Scale

| Token          | Font Family   | Size   | Weight | Line Height | Letter Spacing |
|---------------|---------------|--------|--------|-------------|----------------|
| `headline-lg`  | Kalam         | 48px   | 700    | 1.2         | —              |
| `headline-md`  | Kalam         | 32px   | 700    | 1.2         | —              |
| `headline-sm`  | Kalam         | 24px   | 700    | 1.3         | —              |
| `body-lg`      | Patrick Hand  | 20px   | 400    | 1.5         | —              |
| `body-md`      | Patrick Hand  | 18px   | 400    | 1.5         | —              |
| `label-md`     | Patrick Hand  | 16px   | 400    | 1.4         | 0.02em         |

---

## 📐 Shape & Spacing

### Roundness
- **Preset:** `ROUND_EIGHT` (8px base)  
- **Wobbly radius** (custom, không thể dùng Tailwind):  
  ```css
  --wobbly-radius:     30px 20px 28px 22px / 26px 28px 20px 30px;
  --wobbly-radius-alt: 22px 30px 18px 28px / 30px 18px 28px 20px;
  --wobbly-radius-btn: 50px 46px 50px 46px / 46px 50px 46px 50px;
  ```

### Spacing Scale (Spacing Scale = 2)

| Token    | Value    |
|---------|----------|
| `xs`     | 0.5rem   |
| `sm`     | 1rem     |
| `md`     | 1.5rem   |
| `lg`     | 2.5rem   |
| `xl`     | 4rem     |
| `gutter` | 24px     |
| `margin` | 32px     |

---

## 🖼️ Elevation & Shadow

Độ sâu được thể hiện qua **Hard Offset Shadows** (không dùng blur):

| Class              | CSS Value                          |
|-------------------|------------------------------------|
| `shadow-sketch`    | `4px 4px 0px 0px #2d2d2d`         |
| `shadow-sketch-md` | `6px 6px 0px 0px #2d2d2d`         |
| `shadow-sketch-lg` | `8px 8px 0px 0px #2d2d2d`         |
| `shadow-sketch-red`| `4px 4px 0px 0px #ff4d4d`         |
| `shadow-sketch-blue`| `4px 4px 0px 0px #2d5da1`        |
| `shadow-pressed`   | `0px 0px 0px 0px #2d2d2d`         |

> **Active state:** Shadow về `0px`, element dịch chuyển `translate(4px, 4px)` để mô phỏng nút bị nhấn xuống giấy.

---

## 🧩 Nguyên Tắc Thiết Kế

### Aesthetic: Tactile / Brutalist Hand-Drawn
- **Không có đường thẳng hoàn hảo** — dùng wobbly border-radius
- **Jitter Principle** — xoay nhẹ các container `-1deg` → `1deg`
- **Warm Paper background** — nền `#fbf9f5` với dot-matrix pattern
- **Hard shadows** thay vì gaussian blur

### Màu sắc
- **#ff4d4d** (Red Marker) — Chỉ dùng cho CTA và highlight quan trọng
- **#2d5da1** (Blue Pen) — Link, secondary action, annotation
- **#2d2d2d** (Pencil Black) — Text chính, border, stroke (không dùng pure black `#000`)

### Components
- **Buttons**: Oval wobbly, 2px pencil border, 4px hard shadow  
- **Cards**: Xoay `±1deg`, có tape decoration, pinned thumbtack  
- **Inputs**: Underline style, focus → border dày hơn và chuyển sang blue ink  
- **Lists**: Custom bullet (không dùng browser default dot)

### Color Mode
- **Light mode** · Background: `#fbf9f5`  
- Variant: `FIDELITY` (màu trung thực, không bão hòa quá mức)

---

## 📁 File tham chiếu

| File | Vai trò |
|------|---------|
| `src/app/globals.css` | Tailwind v4 + custom tokens + base styles |
| `src/components/Navbar.tsx` | Navigation bar |
| `src/components/Footer.tsx` | Footer |
| `src/app/page.tsx` | Landing page |
| `src/app/chat/ChatUI.tsx` | Chat interface |
| `src/app/profile/page.tsx` | Profile + Radar chart |
| `src/app/login/page.tsx` | Login page |
| `src/app/signup/page.tsx` | Sign up page |
