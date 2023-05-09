const items = Array.prototype.slice.call(document.getElementsByClassName('news-single'))
let tmpItems = [...items]
const categoryTree = $('#categoryTree')
const titleFilter = $('#titleFilter')
const categoryFilter = $('#categoryFilter')


$('.news-pagination').pagination({
    pageSize: 1,
    dataSource: $('.news-single').toArray(),
    callback: function (data, pagination) {
        renderTemplate(data)
    }
})

function renderTemplate(items) {
    console.log('Creating items...')
    const templates = []

    for (let i = 0; i < items.length; i++) {
        console.log(items[i].dataset.detailUrl)
        console.log(items[i].dataset)
        const item = items[i].dataset
        let template = `<div class="col-span-full lg:col-span-4 news-single"
                               data-detail-url="${item.detailUrl}"
                               data-image-url="${item.imageUrl}"
                               data-category-name="${item.category}}"
                               data-title="${item.title}">
                            <div class="flex flex-col">
                               <a href="${item.detailUrl}"><img
                                  class="rounded-sm"
                                  src="${item.imageUrl}"
                                  alt=""></a>
                               <ul class="filters text-single--filters flex flex-wrap pt-5">
                                  <li>
                                     <a href="${item.detailUrl}">${item.category}</a>
                                  </li>
                               </ul>
                               <div class="text-h3 pt-4">
                                  <a href="${item.detailUrl}">
                                     <h3>${item.title}</h3>
                                  </a>
                               </div>
                            </div>`
        templates.push(template)
    }

    const mainContainer = $('div.posts-main')
    mainContainer.find('.news-single').each(function () {
        $(this).remove()
    })
    for (let i = 0; i < templates.length; i++) {
        $('.posts-main').append(templates[i])
    }
    tmpItems = Array.prototype.slice.call(document.getElementsByClassName('news-single'))
}


function filterItemsTitles(title) {
    const filteredItems = items.filter((el) => {
        return el.dataset.title.includes(title)
    })
    renderTemplate(filteredItems)
}

function filterItemsCategories(categories) {
    const filteredItems = items.filter((el) => {
        return categories.includes(el.dataset.itemCategory)
    })
    const sorted = filteredItems.sort(sortItemsByProp('-itemCreated'))
    console.log(sorted)
    //  createItemPage(sorted)
}


function resetFilters() {
    // createItemPage(items)
}


titleFilter.keyup(function (e) {
    const currentValue = $(this).val().toLowerCase()
    if (e.key === 'Enter' || e.keyCode === 13) {
        filterItemsTitles(currentValue)
    } else if (currentValue.length === 0) {
        filterItemsTitles(currentValue)
    }
})

$('#titleFilterBtn').click(function (e) {
    filterItemsTitles(titleFilter.val().toLowerCase())
    return false
})

categoryFilter.keyup(function (e) {
    const keyCode = e.keyCode || e.which
    const currentValue = $(this).val()

    if (e.key === 'Enter' || keyCode === 13) {
        const found = categoryTree.treeview('search', [currentValue, {
            ignoreCase: true,
            exactMatch: false,
            revealResults: true,
        }])
    } else if (currentValue.length === 0) {
        categoryTree.treeview('clearSearch')
        categoryTree.treeview('collapseAll', {silent: true})
        categoryTree.treeview('expandNode', [0, {silent: true}])
    }
})

$('#categoryFilterBtn').click(function (e) {
    const currentValue = categoryFilter.val()
    if (currentValue.length > 0) {
        const found = categoryTree.treeview('search', [currentValue, {
            ignoreCase: true,
            exactMatch: false,
            revealResults: true,
        }])
    }

    return false
})

function getFullCategoryList(node) {
    const ids = [node.customId]

    if (node.nodes !== undefined && node.nodes.length > 0) {
        for (let i = 0; i < node.nodes.length; i++) {
            ids.push(...getFullCategoryList(node.nodes[i]))
        }
    }

    return ids
}

function initCategories(categoriesListUrl, informationTypeId) {
    $.get({
        url: categoriesListUrl,   // '/platform/kb/category/names/'
        data: {name: '', 'information_type__id': informationTypeId},
        success: (data, textStatus, jqXHR) => {
            function formatCategory(category) {
                let categoryNode = {
                    text: category.name,
                    customId: `${category.id}`
                }

                if (category.parent_tree.length > 0) {
                    categoryNode['nodes'] = []
                    for (let i = 0; i < category.parent_tree.length; i++) {
                        categoryNode['nodes'].push(formatCategory(category.parent_tree[i]))
                    }
                }

                return categoryNode
            }

            let tree = [{
                text: 'Kategorie',
                customId: "-1",
                nodes: [],
                state: {
                    expanded: true,
                }
            }]
            for (let i = 0; i < data.length; i++) {
                if (data[i].parent_category === null) {
                    tree[0].nodes.push(formatCategory(data[i]))
                }
            }

            categoryTree.treeview({
                data: tree,
                levels: 0,
                onhoverColor: '#9CDFC0',
                selectedBackColor: '#23C678',
                searchResultColor: '#1fcb3c',
                onNodeSelected: function (event, node) {
                    if (node.text === 'Kategorie' && node.nodeId === 0) {
                        categoryTree.treeview('unselectNode', [node.nodeId, {silent: true}])
                    } else {
                        categoryFilter.attr('placeholder', 'Kategoria: ' + node.text)
                        //categoryTree.treeview('collapseAll')

                        const categoriesInNode = getFullCategoryList(node)

                        filterItemsCategories(categoriesInNode)
                    }
                },
                onNodeUnselected: function (event, node) {
                    if (node.text !== 'Kategorie' && node.nodeId !== 0) {
                        // wait to check if there was no another selection
                        setTimeout(() => {
                            categoryFilter.attr('placeholder', 'Szukaj kategorii...')

                            if (categoryTree.treeview('getSelected').length === 0) {
                                const sorted = items.sort(sortItemsByProp('-itemCreated'))

                                // createItemPage(sorted)
                            }
                        }, 100)
                        /*setTimeout(() => {
                            console.log('250')
                            console.log(categoryTree.treeview('getSelected').length > 0)
                        }, 250)*/
                    }
                },
                onNodeExpanded: function (event, node) {
                    if (node.text === 'Kategorie' && node.nodeId === 0) {
                        categoryTree.css('border', '2px solid #23c678')
                    }
                },
                onNodeCollapsed: function (event, node) {
                    if (node.text === 'Kategorie' && node.nodeId === 0) {
                        categoryTree.treeview('expandNode', [node.nodeId, {silent: true}])
                    }
                }
            })
        }
    })
}

window.onload = function (e) {
    const dateSortSelect = $('#sortSelect')
    dateSortSelect.change(function () {
        if ($(this).val() === '0') {
            console.log('Najnowsze')
            const sorted = tmpItems.sort(sortItemsByProp('-itemCreated'))
            // createItemPage(sorted)
        } else {
            console.log('Najstarsze')
            const sorted = tmpItems.sort(sortItemsByProp('itemCreated'))
            // createItemPage(sorted)
        }
    })
    dateSortSelect.trigger('change')
}