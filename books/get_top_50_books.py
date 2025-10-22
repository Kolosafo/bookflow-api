from .utils import search_books
top_50 = [
  "intitle:The+7+Habits+of+Highly+Effective+People+inauthor:Stephen+Covey",
  "intitle:Atomic+Habits+inauthor:James+Clear",
  "intitle:Think+and+Grow+Rich+inauthor:Napoleon+Hill",
  "intitle:Mindset+inauthor:Carol+Dweck",
  "intitle:Grit+inauthor:Angela+Duckworth",
  "intitle:The+Power+of+Now+inauthor:Eckhart+Tolle",
  "intitle:The+Subtle+Art+of+Not+Giving+a+Fuck+inauthor:Mark+Manson",
  "intitle:Daring+Greatly+inauthor:Brene+Brown",
  "intitle:Man's+Search+for+Meaning+inauthor:Viktor+Frankl",
  "intitle:The+Four+Agreements+inauthor:Don+Miguel+Ruiz",
  "intitle:Rich+Dad+Poor+Dad+inauthor:Robert+Kiyosaki",
  "intitle:The+Richest+Man+in+Babylon+inauthor:George+Clason",
  "intitle:You+Only+Live+Once+inauthor:Jason+Vitug",
  "intitle:I+Will+Teach+You+To+Be+Rich+inauthor:Ramit+Sethi",
  "intitle:The+Psychology+of+Money+inauthor:Morgan+Housel",
  "intitle:The+Millionaire+Next+Door+inauthor:Thomas+Stanley",
  "intitle:Money+Master+the+Game+inauthor:Tony+Robbins",
  "intitle:The+Total+Money+Makeover+inauthor:Dave+Ramsey",
  "intitle:The+Simple+Path+to+Wealth+inauthor:JL+Collins",
  "intitle:How+to+Win+Friends+and+Influence+People+inauthor:Dale+Carnegie",
  "intitle:Emotional+Intelligence+inauthor:Daniel+Goleman",
  "intitle:Influence+inauthor:Robert+Cialdini",
  "intitle:Crucial+Conversations+inauthor:Joseph+Grenny",
  "intitle:Never+Split+the+Difference+inauthor:Chris+Voss",
  "intitle:Thinking+Fast+and+Slow+inauthor:Daniel+Kahneman",
  "intitle:The+Laws+of+Human+Nature+inauthor:Robert+Greene",
  "intitle:The+Art+of+Communicating+inauthor:Thich+Nhat+Hanh",
  "intitle:Nonviolent+Communication+inauthor:Marshall+Rosenberg",
  "intitle:Drive+inauthor:Daniel+Pink",
  "intitle:The+Lean+Startup+inauthor:Eric+Ries",
  "intitle:Zero+to+One+inauthor:Peter+Thiel",
  "intitle:Good+to+Great+inauthor:Jim+Collins",
  "intitle:Start+with+Why+inauthor:Simon+Sinek",
  "intitle:The+Innovator's+Dilemma+inauthor:Clayton+Christensen",
  "intitle:Principles+inauthor:Ray+Dalio",
  "intitle:The+Hard+Thing+About+Hard+Things+inauthor:Ben+Horowitz",
  "intitle:The+E-Myth+Revisited+inauthor:Michael+Gerber",
  "intitle:Blue+Ocean+Strategy+inauthor:W+Chan+Kim",
  "intitle:Measure+What+Matters+inauthor:John+Doerr",
  "intitle:Deep+Work+inauthor:Cal+Newport",
  "intitle:Essentialism+inauthor:Greg+McKeown",
  "intitle:The+One+Thing+inauthor:Gary+Keller",
  "intitle:Eat+That+Frog+inauthor:Brian+Tracy",
  "intitle:Getting+Things+Done+inauthor:David+Allen",
  "intitle:The+Power+of+Full+Engagement+inauthor:Jim+Loehr",
  "intitle:The+5+AM+Club+inauthor:Robin+Sharma",
  "intitle:The+Compound+Effect+inauthor:Darren+Hardy",
  "intitle:Make+Time+inauthor:Jake+Knapp"
]

def get_top_50():
    result = []
    for book in top_50:
        get_book = search_books(book, 1)
        result.append(get_book)
    
    return result

