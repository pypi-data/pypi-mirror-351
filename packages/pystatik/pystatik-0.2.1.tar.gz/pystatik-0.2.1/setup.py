from setuptools import setup, find_packages

setup(
    name='pystatik',  # Kütüphane adı (PyPI'de görünür)
    version='0.2.1',  # İlk sürüm
    description='Türkçe fonksiyonlarla sade istatistik kütüphanesi',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Poyraz',  # İstersen tam adını yazabilirsin
    author_email='poyraz@example.com',  # Dilersen geçici bir mail yaz
    url='https://github.com/kullaniciadi/pystatic',  # GitHub reposu (opsiyonel)
    packages=find_packages(),  # Tüm klasörleri içeri al
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Intended Audience :: Education',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    keywords='istatistik python türkçe egitim medyan ortalama sapma mod',  # Arama için etiketler
    python_requires='>=3.6',
)
