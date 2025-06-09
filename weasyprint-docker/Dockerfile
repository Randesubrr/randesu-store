FROM python:3.10

RUN echo "deb http://deb.debian.org/debian/ buster main contrib non-free" > /etc/apt/sources.list

# Install dependencies for WeasyPrint
RUN apt-get update && apt-get install -y \
    libglib2.0-dev \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    libfontconfig1 \
    libfreetype6 \
    libssl-dev \
    libgtk-3-0


# Install WeasyPrint via pip
RUN pip install weasyprint

# Set default command to bash
CMD ["bash"]
