(define (my-watermark 
aimg adraw wmfile scale off opai)
    (let*
        (
            ; Get filename
            (dirs (strbreakup wmfile "/"))
            (depthofpath (length dirs))
            (wmfilename (nth (- depthofpath 1) dirs))
            ; Get photo image resolution
            (img (car (gimp-item-get-image adraw)))
            (imgw (car (gimp-image-width img)))
            (imgh (car (gimp-image-height img)))
            ; Load watermark file & get resolution
            (wmimage (car (gimp-file-load RUN-NONINTERACTIVE wmfile wmfilename)))
            (wmw (car (gimp-image-width wmimage)))
            (wmh (car (gimp-image-height wmimage)))
            ; Get drawable of watermark & copy to buffer
            (wmdrawable (car (gimp-image-get-active-layer wmimage)))
            (copied (gimp-edit-copy wmdrawable))
            ; Paste watermark from buffer & get the watermark layer
            (wmlayer (car (gimp-edit-paste adraw TRUE)))
            ; Get scaled resolution for watermark
            (rwmw (/ imgw scale))
            (rwmh (/ (* rwmw wmh) wmw))
            ; Get offset margin for watermark
            (offx (- (- imgw rwmw) (* off imgw)))
            (offy (- (- imgh rwmh) (* off imgh)))
        )
        ; Scale the watermark
        (gimp-layer-scale wmlayer rwmw rwmh FALSE)
        ; Offset the watermark
        (gimp-layer-set-offsets wmlayer offx offy)
        ; Set opacity for watermark
        (gimp-layer-set-opacity wmlayer opai)
        ; Add watermark as a layer
        (gimp-floating-sel-to-layer wmlayer)
        ; Set layer name
        (gimp-item-set-name wmlayer "watermark")
        ; Flush display
        (gimp-displays-flush)
    )
)

(script-fu-register 
    "my-watermark"
    "Add my watermark"
    "A simple script adds image watermark."
    "Manoj Kumar"
    "(c) GPL V3.0 or later"
    "Jan 2024"
    "RGB*"
    SF-IMAGE       "Image"                     0
    SF-DRAWABLE    "Drawable"                  0
    SF-FILENAME    "Watermark image"           ""
    SF-ADJUSTMENT  "Watermark scale factor (/)"    '(10 1 100 1 10 0 1)
    SF-ADJUSTMENT  "Offset margin (%)"             '(0.005 0.000 0.100 0.001 0.005 3 1)
    SF-ADJUSTMENT  "Image opacity (%)"             '(30 1 100 1 10 0 1)
)

(script-fu-menu-register "my-watermark" "<Image>/Filters/Watermarks/")
