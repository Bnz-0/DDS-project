const { APKG } = require('anki-apkg')
const fs = require("fs")
var showdown  = require('showdown'),
    mdconverter = new showdown.Converter()

const SPLIT_TOKEN = 'FRONTBACKFRONTBACKFRONTBACKFRONTBACKFRONTBACKFRONTBACKFRONTBACK\n'

if (process.argv.length < 2) {
  console.log("Please provide the name of a package to build")
  process.exit(1)
}

DECK_NAME = process.argv[2]
DECK_TO_BUILD = process.cwd() + '/' + DECK_NAME
CARDS_TO_BUILD = DECK_TO_BUILD + '/cards/'
MEDIA_TO_BUILD = DECK_TO_BUILD + '/media/'

console.log("deck to build " + DECK_TO_BUILD)
console.log("cards to build " + CARDS_TO_BUILD)

const apkg = new APKG({
  name: DECK_NAME,
  card: {
      fields: ['word', 'meaning', 'usage'],
      template: {
          question: '{{word}}',
          answer: `
            <div class="word">{{word}}</div>
            <div class="definition">{{meaning}}</div>
            <div class="usage">{{usage}}</div>
          `
      },
      styleText: '.card { text-align: center; } .definition{ width:80%; margin:auto; text-align: left; font-size:25px; }'
    }
  })

function BuildApkg() {

  fs.readdir(CARDS_TO_BUILD, function(err, cards) {
    if (err) throw err

    for ( let i = 0; i < cards.length ; ++i ) {
      let filename = cards[i]
      let IS_MARKDOWN = filename.substr(filename.lastIndexOf('.')+1, filename.length) === 'md';

      fs.readFile(CARDS_TO_BUILD + filename, 'utf8', function(err, data) {
        if (err) throw err;
        let l = data.split(SPLIT_TOKEN)

        let front = IS_MARKDOWN? mdconverter.makeHtml(l[0]) : l[0]
        let back  = IS_MARKDOWN? mdconverter.makeHtml(l[1]) : l[1]

        console.log("adding:", IS_MARKDOWN? "md":"no", front)

        apkg.addCard({
          timestamp: +new Date(), // create time
          content: [front, back, 'sample usage'] // keep the order same as `fields` defined above
        })

      });
    }


    fs.readdir(MEDIA_TO_BUILD, function(err, medias) {
        if (err) throw err;

        for ( let i = 0; i < medias.length ; ++i ) {
          let filename = medias[i]    
          console.log(apkg.addMedia)
          apkg.addMedia(filename, fs.readFileSync(MEDIA_TO_BUILD + filename))
        }

        apkg.save(process.cwd())
    })
  })
}



fs.access(DECK_TO_BUILD, function(error) {
  if (error) {
    console.log("No folder " + DECK_NAME + " found!")
  } else {
    fs.access(DECK_TO_BUILD, function(error) {
      if (error) {
        console.log("No cards folder in " + DECK_NAME + " was found!")
      } else {
        BuildApkg();
      }
    })
  }
})

