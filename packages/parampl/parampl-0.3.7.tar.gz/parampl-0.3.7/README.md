# parampl
Write formatted paragraphs in matplotlib

```
from parampl import ParaMPL
from lorem_text import lorem

f, ax = plt.subplots()
parampl = ParaMPL(ax, spacing=0.3, fontsize=9)

parampl.write(lorem.paragraph(), (0.05, 0.95),
              avoid_left_of =[(0.2, (0.3, 0.5)),
                              (0.3, (0.4, 0.7))],
              avoid_right_of = (0.8, (0.3, 0.7),
              width=0.7, justify='full',
             )
```

![Sample with 'full' justification and avoid areas](https://github.com/duckrojo/parampl/blob/master/sample_full.png?raw=true)
(Full example code in quickstart.py)