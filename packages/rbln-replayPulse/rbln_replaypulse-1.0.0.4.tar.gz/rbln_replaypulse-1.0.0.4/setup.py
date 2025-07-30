import setuptools


setuptools.setup(
    name="rbln_replayPulse",
    version="1.0.0.4",
    description="RBLN-replayPulse",
    author="sykim",
    author_email="sungyeon0143@gmail.com",
    packages=['rbln_replayPulse'],
    python_requires='>=3',
    install_requires=[
        'pandas',
        'matplotlib',
        'pytz'
    ],
    entry_points={
        'console_scripts': [
            'rbln-replayPulse = rbln_replayPulse.main:main'
        ]
    }
)
