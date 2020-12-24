from json_storage import JsonStorage
import functions
import states


storage = JsonStorage("db", states.GREET)

conversation = {
    states.GREET: [
        ('.+', functions.greet)
    ],
    states.MAIN: [
        ('[Сс]татистик.*', functions.stats),
        ('([Пп]омощь)|([Пп]равила)', functions.help),
        ('[Сс]вязь', functions.support)
    ],
    states.ASKED: [
        ('.+', functions.check_answer)
    ],
    states.FINISHED: [
        ('[Сс]вязь', functions.support),
        ('.*', functions.support_only)
    ]
}

fallbacks = [
    (".*", functions.fallback)
]

"""
states.MET: [
    ['^[^/].+', functions.go_on],
    ['/stop', functions.stop]
]
"""