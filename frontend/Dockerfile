# Giai đoạn 1: Build ứng dụng React
FROM node:18-alpine AS build

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy file package.json và package-lock.json
COPY package.json ./
COPY package-lock.json ./

# Cài đặt các dependencies
RUN npm install

# Copy toàn bộ source code của ứng dụng
COPY . .

# Build ứng dụng
RUN npm run build

# Giai đoạn 2: Phục vụ ứng dụng bằng Nginx
FROM nginx:stable-alpine

# Copy kết quả build từ giai đoạn build vào thư mục web root của Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copy cấu hình Nginx tùy chỉnh
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Mở cổng 80
EXPOSE 80

# Khởi động Nginx
CMD ["nginx", "-g", "daemon off;"]
