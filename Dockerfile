# 使用Python 3.12作为基础镜像
FROM python:3.12-slim-bookworm

# 设置工作目录
WORKDIR /app

# 创建新的 sources.list 文件，使用中科大镜像源
RUN echo "deb https://mirrors.ustc.edu.cn/debian/ bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list

# 安装系统依赖、Inkscape、字体和 WeasyPrint 依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libx264-dev \
    libfreetype6-dev \
    libjpeg-dev \
    libpng-dev \
    wget \
    inkscape \
    fonts-noto-cjk \
    libglib2.0-0 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    libffi8 \
    curl \
    && rm -rf /var/lib/apt/lists/*


# 复制requirements.txt文件
COPY requirements.txt .

# 使用pip镜像并安装Python依赖
RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple \
    && pip install --no-cache-dir -r requirements.txt

# 复制项目文件到工作目录
COPY . .

# 刷新字体缓存
RUN fc-cache -fv

# 暴露端口8008
EXPOSE 8008

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8008"]
