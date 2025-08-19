# 使用Python 3.12作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 创建新的 sources.list 文件，使用中科大镜像源
RUN echo "deb https://mirrors.ustc.edu.cn/debian/ bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list

# 安装系统依赖、Chrome、Inkscape、curl 和 Playwright 依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libx264-dev \
    libfreetype6-dev \
    libjpeg-dev \
    libpng-dev \
    wget \
    gnupg \
    inkscape \
    fonts-noto-cjk \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*


# 复制requirements.txt文件
COPY requirements.txt .

# 使用pip镜像并安装Python依赖
RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple \
    && pip install --no-cache-dir -r requirements.txt

# 安装 Playwright
RUN playwright install firefox

# 设置时区为Asia/Shanghai
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 复制项目文件到工作目录
COPY . .

# 刷新字体缓存
RUN fc-cache -fv

# 暴露端口8008
EXPOSE 8008

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8008"]
