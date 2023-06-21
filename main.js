
const params = new URLSearchParams(window.location.search)

const gameCount = parseInt(params.get('games')) || 4  // How many games to put in screen. Cards are 2x the amount of games.
const repeatGames = params.get('repeat') != null  // DEBUG: Optionally repeat the games to fill with synthetic content

const games = []

function shuffleInPlace(arr) {
    let cur = arr.length
    while (cur > 0) {
        const rand = Math.floor(Math.random() * cur)
        cur -= 1
        const tmp = arr[cur]
        arr[cur] = arr[rand]
        arr[rand] = tmp
    }
}

function getShownCards() {
    const shown = []
    for (const g of games) {
        if (g.won) continue
        for (const kind in g.cards) {
            if (g.cards[kind].shown) {
                shown.push(g.cards[kind])
            }
        }
    }
    return shown
}

function setMessage(txt, color = 'black') {
    const msgElem = document.getElementById('message-box')
    msgElem.innerHTML = txt
    msgElem.style.color = color
}

function setShown(card, shown) {
    card.shown = shown
    card.contentsElem.style.opacity = shown ? 1 : 0
}

function wonPair(game) {
    game.won = true
    for (const kind in game.cards) {
        const card = game.cards[kind]
        card.cardElem.style.backgroundColor = "#D0F0D0"
    }
    let wonAll = true
    for (const g of games) {
        if (!g.won) wonAll = false
    }
    if (wonAll) {
        setMessage("Felicitaciones, encontraste todos los pares!<br><a href=\"javascript:window.location.reload()\">Jugar de nuevo</a> <a href=\"?games=" + Math.round(gameCount * 1.1 + 2) + "\">Más difícil</a>")
    } else {
        setMessage("Felicitaciones, encontraste un par!<br>Toca otra tarjeta para seguir jugando.")
    }
}

function lostPair() {
    setMessage("Esas tarjetas no calzan :(<br>Toca cualquier tarjeta para volver a intentarlo.")
}

function onCardClick(gameId, kind) {
    const game = games[gameId]
    console.log(`clicked on ${kind} card of game ${game.title}`)
    if (game.won) return

    const card = game.cards[kind]
    const otherCard = game.cards[kind === 'title' ? 'desc' : 'title']

    let shownCards = getShownCards()

    if (shownCards.length === 2) {
        for (const card of shownCards) {
            setShown(card, false)
        }
        setMessage("Toca una tarjeta.")
        return
    }

    setShown(card, !card.shown)

    shownCards = getShownCards()
    if (shownCards.length === 2) {
        if (shownCards[0].id === shownCards[1].id) {
            wonPair(game)
        } else {
            lostPair()
        }
    } else if (shownCards.length === 1) {
        setMessage("Toca otra tarjeta.")
    } else {
        // shownCards.length === 0
        setMessage("Toca una tarjeta.")
    }
}

function createCard(id, kind) {
    const card = document.createElement('div')
    card.classList.add('card')
    card.addEventListener('click', () => {
        onCardClick(id, kind)
    })

    const contents = document.createElement('div')
    contents.style.opacity = 0
    contents.classList.add('card-contents')
    card.appendChild(contents)

    return {
        id,
        kind,
        shown: false,
        cardElem: card,
        contentsElem: contents,
    }
}

function createGame(gameData) {
    const id = games.length

    const titleCard = createCard(id, 'title')

    const imageElem = document.createElement('img')
    imageElem.width = 120
    imageElem.height = 120
    imageElem.draggable = false
    imageElem.src = gameData.image
    imageElem.classList.add('card-image')
    titleCard.contentsElem.appendChild(imageElem)

    const titleElem = document.createElement('p')
    titleElem.innerText = gameData.title
    titleElem.classList.add('card-title')
    titleCard.contentsElem.appendChild(titleElem)

    const descCard = createCard(id, 'desc')

    descCard.contentsElem.classList.add('card-desc')
    descCard.contentsElem.innerText = gameData.desc

    const game = {
        id,
        image: gameData.image,
        title: gameData.title,
        desc: gameData.desc,
        won: false,
        cards: {
            title: titleCard,
            desc: descCard,
        },
    }
    games.push(game)
}

window.addEventListener('load', () => {
    const grid = document.getElementById('root-grid')

    // Choose gameCount random games and create their cards
    let someGames = rawGameData.slice()
    if (repeatGames) {
        const pool = rawGameData.slice()
        shuffleInPlace(pool)
        let i = 0
        let version = 2
        while (someGames.length < gameCount) {
            const game = pool[i]
            someGames.push({
                image: game.image,
                title: game.title + ` (versión ${version})`,
                desc: game.desc + ` (versión ${version})`,
            })
            i += 1
            if (i === pool.length) {
                i = 0
                version += 1
            }
        }
    }
    shuffleInPlace(someGames)
    for (const game of someGames.slice(0, gameCount)) {
        createGame(game)
    }

    // Build cards with the two cards of each item
    const cards = []
    for (const game of games) {
        for (const kind in game.cards) {
            cards.push(game.cards[kind])
        }
    }

    // Shuffle cards
    shuffleInPlace(cards)

    // Insert random cards
    for (const card of cards) {
        grid.appendChild(card.cardElem)
    }

    setMessage("Toca una tarjeta para empezar.")
})
