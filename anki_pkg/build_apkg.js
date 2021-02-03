const AnkiExport = require('anki-apkg-export').default;
const fs = require("fs")
var showdown  = require('showdown')
var showdownKatex  = require('showdown-katex')
var 
mdconverter = new showdown.Converter({
    extensions: [
      showdownKatex({
        // maybe you want katex to throwOnError
        throwOnError: true,
        // disable displayMode
        displayMode: false,
        // change errorColor to blue
        errorColor: '#1500ff',
      }),
    ],
  });
mdconverter.makeHtml('~x=2~');


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

const apkg = new AnkiExport(DECK_NAME);

function BuildFront(s) {
  return "<div>" + s + "</div>"
}

function BuildBack(s) {
  return '<div style="width:80%; margin:auto; text-align: left; font-size:20px;">' + 
          s + 
          "</div>"
}


function BuildApkg() {

  fs.readdir(CARDS_TO_BUILD, function(err, cards) {
    if (err) throw err

    console.log(`importing ${cards.length} cards`)

    for ( let i = 0; i < cards.length ; ++i ) {
      let filename = cards[i]
      let IS_MARKDOWN = filename.substr(filename.lastIndexOf('.')+1, filename.length) === 'md';

      data = fs.readFileSync(CARDS_TO_BUILD + filename, {encoding: 'utf-8'})
      let l = data.split(SPLIT_TOKEN)

      let front = IS_MARKDOWN? mdconverter.makeHtml(l[0]) : l[0]
      let back  = IS_MARKDOWN? mdconverter.makeHtml(l[1]) : l[1]

      apkg.addCard(BuildFront(front), BuildBack(back))
    }


    fs.readdir(MEDIA_TO_BUILD, function(err, medias) {
        if (err) throw err;

        for ( let i = 0; i < medias.length ; ++i ) {
          let filename = medias[i]    
          apkg.addMedia(filename, fs.readFileSync(MEDIA_TO_BUILD + filename))
        }

        apkg.save()
        .then(zip => {
          fs.writeFileSync( process.cwd() + '/' + DECK_NAME + '.apkg', zip, 'binary');
          console.log(`Package has been generated: ${DECK_NAME}.pkg`);
        })
        .catch(err => console.log(err.stack || err));
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

